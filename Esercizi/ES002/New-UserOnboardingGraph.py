"""
New-UserOnboardingGraph.py

Onboarding script using Microsoft Graph (MSAL + REST) to perform mailbox/user configuration
- Auth: Client credentials (recommended for automation) or Device Code (interactive)
- Actions performed (where available via Graph):
  - Verify user exists
  - Update user attributes (department, officeLocation)
  - Set manager (by email)
  - Update mailboxSettings (timeZone, language, autoReplies)
  - Add user to distribution groups

Limitations:
- Some Exchange-specific operations (enable archive, detailed Exchange policies, mailbox quotas, audit settings) are not available via Microsoft Graph and still require Exchange PowerShell or Graph API endpoints with corresponding support.

Prerequisites:
- pip install msal requests
- An app registration with appropriate Graph permissions (User.ReadWrite.All, Group.ReadWrite.All, Directory.Read.All or application equivalents)

Usage examples:
python New-UserOnboardingGraph.py --user mario.rossi@contoso.com --display-name "Mario Rossi" --manager supervisor@contoso.com --groups "IT-Team" "All-Employees" --tenant YOUR_TENANT_ID --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET

Or for interactive device code (no client secret):
python New-UserOnboardingGraph.py --user mario.rossi@contoso.com --display-name "Mario Rossi" --tenant YOUR_TENANT_ID --client-id YOUR_CLIENT_ID
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional

import requests
from msal import ConfidentialClientApplication, PublicClientApplication

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("onboarding-graph")

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_SCOPE = ["https://graph.microsoft.com/.default"]


def acquire_token(client_id: str, tenant_id: str, client_secret: Optional[str]) -> str:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    if client_secret:
        app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
        result = app.acquire_token_for_client(scopes=DEFAULT_SCOPE)
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(f"Unable to acquire token (client credentials): {result.get('error_description') or result}")
    else:
        app = PublicClientApplication(client_id, authority=authority)
        flow = app.initiate_device_flow(scopes=["User.ReadWrite.All", "Group.ReadWrite.All", "Directory.Read.All"])
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to start device flow: {flow}")
        print(flow["message"])  # instruct user to authenticate
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(f"Unable to acquire token (device code): {result.get('error_description') or result}")


def graph_get(path: str, token: str, params: Optional[Dict] = None) -> Dict:
    url = GRAPH_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()


def graph_post(path: str, token: str, data: Dict) -> Dict:
    url = GRAPH_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=data)
    r.raise_for_status()
    return r.json() if r.content else {}


def graph_patch(path: str, token: str, data: Dict) -> None:
    url = GRAPH_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.patch(url, headers=headers, json=data)
    r.raise_for_status()


def find_user_by_upn(upn: str, token: str) -> Optional[Dict]:
    try:
        return graph_get(f"/users/{upn}", token)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise


def find_user_by_email(email: str, token: str) -> Optional[Dict]:
    res = graph_get(f"/users", token, params={"$filter": f"mail eq '{email}' or userPrincipalName eq '{email}'"})
    if res.get("value"):
        return res["value"][0]
    return None


def find_group_by_display_name(name: str, token: str) -> Optional[Dict]:
    res = graph_get(f"/groups", token, params={"$filter": f"displayName eq '{name}'"})
    if res.get("value"):
        return res["value"][0]
    return None


def add_user_to_group(user_id: str, group_id: str, token: str) -> None:
    path = f"/groups/{group_id}/members/$ref"
    data = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"}
    # Some responses return 204 No Content
    url = GRAPH_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=data)
    if r.status_code not in (204, 201):
        r.raise_for_status()


def set_manager(user_id: str, manager_id: str, token: str) -> None:
    path = f"/users/{user_id}/manager/$ref"
    data = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{manager_id}"}
    url = GRAPH_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.put(url, headers=headers, json=data)
    r.raise_for_status()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Onboard a user in Microsoft 365 via Microsoft Graph")
    parser.add_argument("--user", required=True, help="UserPrincipalName of the user")
    parser.add_argument("--display-name", required=True, help="Display name")
    parser.add_argument("--manager", help="Manager email")
    parser.add_argument("--department", help="Department")
    parser.add_argument("--office", help="Office location")
    parser.add_argument("--groups", nargs="*", help="Distribution groups to add the user to (by display name)")
    parser.add_argument("--tenant", required=True, help="Tenant ID (GUID) or tenant name")
    parser.add_argument("--client-id", required=True, help="App (client) ID")
    parser.add_argument("--client-secret", help="Client secret (omit to use device code interactive auth)")
    parser.add_argument("--lang", default="it-IT", help="Locale for mailbox (default it-IT)")
    parser.add_argument("--tz", default="W. Europe Standard Time", help="Time zone for mailbox (default W. Europe Standard Time)")

    args = parser.parse_args(argv)

    try:
        token = acquire_token(args.client_id, args.tenant, args.client_secret or os.environ.get("AZURE_CLIENT_SECRET"))
        logger.info("Token acquisito con successo")

        user = find_user_by_upn(args.user, token)
        if not user:
            logger.error("Utente non trovato: %s", args.user)
            return 2

        user_id = user["id"]
        logger.info("Utente trovato: %s (id=%s)", args.user, user_id)

        # Update basic attributes
        patch_data = {}
        if args.department:
            patch_data["department"] = args.department
        if args.office:
            patch_data["officeLocation"] = args.office

        if patch_data:
            graph_patch(f"/users/{user_id}", token, patch_data)
            logger.info("Attributi utente aggiornati: %s", json.dumps(patch_data))

        # Set manager if provided
        if args.manager:
            mgr = find_user_by_email(args.manager, token)
            if mgr:
                set_manager(user_id, mgr["id"], token)
                logger.info("Manager impostato: %s", args.manager)
            else:
                logger.warning("Manager non trovato: %s", args.manager)

        # Update mailboxSettings
        mailbox_patch = {
            "timeZone": args.tz,
            "language": {"locale": args.lang, "displayName": args.lang},
            "automaticRepliesSetting": {"status": "disabled"}
        }
        try:
            graph_patch(f"/users/{user_id}/mailboxSettings", token, mailbox_patch)
            logger.info("Mailbox settings aggiornate: %s", json.dumps(mailbox_patch))
        except requests.HTTPError as e:
            # Some tenants or licenses may not allow mailboxSettings updates via Graph
            logger.warning("Non è stato possibile aggiornare mailboxSettings via Graph: %s", e)

        # Add to groups
        if args.groups:
            for gname in args.groups:
                grp = find_group_by_display_name(gname, token)
                if grp:
                    try:
                        add_user_to_group(user_id, grp["id"], token)
                        logger.info("Aggiunto al gruppo: %s", gname)
                    except requests.HTTPError as e:
                        logger.warning("Errore aggiunta a gruppo %s: %s", gname, e)
                else:
                    logger.warning("Gruppo non trovato: %s", gname)

        # Summary
        summary = {
            "success": True,
            "user": args.user,
            "userId": user_id,
            "updatedAttributes": patch_data,
            "groupsRequested": args.groups,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    except Exception as exc:
        logger.exception("Errore durante l'onboarding")
        print(json.dumps({"success": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
