"""
New-UserOnboardingMsGraphSdk.py

Esempio d'uso del Microsoft Graph SDK per Python (msgraph-core) con
azure-identity per l'autenticazione. Questo script mostra come:
 - ottenere un client Graph
 - recuperare un utente (by UPN)
 - aggiornare attributi utente (department, officeLocation)
 - impostare il manager
 - aggiornare mailboxSettings (timeZone, language, automaticReplies)
 - aggiungere l'utente a gruppi

Requisiti:
  pip install msgraph-core azure-identity

Nota sulle limitazioni:
  Alcune operazioni specifiche di Exchange (abilitare archive, impostare quote,
  configurazioni avanzate Exchange) non sono esposte via Graph SDK e richiedono
  Exchange PowerShell o endpoint Graph specifici non sempre disponibili.
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from typing import List, Optional

from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential, DeviceCodeCredential

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("onboarding-msgraph-sdk")

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def get_graph_client(tenant_id: str, client_id: str, client_secret: Optional[str] = None) -> GraphClient:
    """Crea un `GraphClient` usando Client Credentials (se client_secret fornito)
    oppure Device Code interactive (se client_secret omesso).
    """
    if client_secret:
        cred = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        client = GraphClient(credential=cred, scopes=["https://graph.microsoft.com/.default"])
    else:
        # Device code flow per autenticazione interattiva
        cred = DeviceCodeCredential(client_id=client_id, tenant_id=tenant_id)
        client = GraphClient(credential=cred)
    return client


def get_user_by_upn(client: GraphClient, upn: str) -> Optional[dict]:
    res = client.get(f"/users/{upn}")
    if res.status_code == 200:
        return res.json()
    if res.status_code == 404:
        return None
    res.raise_for_status()


def update_user(client: GraphClient, user_id: str, patch: dict) -> None:
    res = client.patch(f"/users/{user_id}", json=patch)
    if res.status_code not in (200, 204):
        res.raise_for_status()


def set_manager(client: GraphClient, user_id: str, manager_id: str) -> None:
    data = {"@odata.id": f"{GRAPH_BASE}/users/{manager_id}"}
    res = client.put(f"/users/{user_id}/manager/$ref", json=data)
    if res.status_code not in (204,):
        res.raise_for_status()


def update_mailbox_settings(client: GraphClient, user_id: str, settings: dict) -> None:
    # mailboxSettings endpoint supports PATCH
    res = client.patch(f"/users/{user_id}/mailboxSettings", json=settings)
    if res.status_code not in (200, 204):
        res.raise_for_status()


def find_group_by_display_name(client: GraphClient, display_name: str) -> Optional[dict]:
    # filtro per displayName (esatto)
    params = {"$filter": f"displayName eq '{display_name}'"}
    res = client.get("/groups", params=params)
    res.raise_for_status()
    body = res.json()
    items = body.get("value", [])
    return items[0] if items else None


def add_user_to_group(client: GraphClient, user_id: str, group_id: str) -> None:
    data = {"@odata.id": f"{GRAPH_BASE}/directoryObjects/{user_id}"}
    res = client.post(f"/groups/{group_id}/members/$ref", json=data)
    if res.status_code not in (201, 204):
        # 400/409 may indicate membership already exists or invalid request
        res.raise_for_status()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Esempio onboarding con Microsoft Graph SDK (msgraph-core)")
    parser.add_argument("--user", required=True, help="UserPrincipalName (es: mario.rossi@contoso.com)")
    parser.add_argument("--display-name", required=True, help="Display name")
    parser.add_argument("--manager", help="Manager email (es: manager@contoso.com)")
    parser.add_argument("--department", help="Department")
    parser.add_argument("--office", help="Office location")
    parser.add_argument("--groups", nargs="*", help="Gruppi (displayName) da aggiungere")
    parser.add_argument("--tenant", required=True, help="Tenant ID o tenant name")
    parser.add_argument("--client-id", required=True, help="Client (app) ID")
    parser.add_argument("--client-secret", help="Client secret (omettendo si userà device code)")
    parser.add_argument("--lang", default="it-IT", help="Locale per mailboxSettings (default it-IT)")
    parser.add_argument("--tz", default="W. Europe Standard Time", help="Time zone per mailboxSettings")

    args = parser.parse_args(argv)

    try:
        client = get_graph_client(args.tenant, args.client_id, args.client_secret)
        logger.info("Graph client creato")

        user = get_user_by_upn(client, args.user)
        if not user:
            logger.error("Utente non trovato: %s", args.user)
            return 2
        user_id = user["id"]
        logger.info("Utente trovato: %s (id=%s)", args.user, user_id)

        # Aggiorna attributi utente
        patch = {}
        if args.department:
            patch["department"] = args.department
        if args.office:
            patch["officeLocation"] = args.office
        if patch:
            update_user(client, user_id, patch)
            logger.info("Attributi aggiornati: %s", patch)

        # Imposta manager se richiesto
        if args.manager:
            mgr = get_user_by_upn(client, args.manager) or None
            if not mgr:
                # prova a cercare per mail
                res = client.get("/users", params={"$filter": f"mail eq '{args.manager}' or userPrincipalName eq '{args.manager}'"})
                res.raise_for_status()
                vals = res.json().get("value", [])
                mgr = vals[0] if vals else None
            if mgr:
                set_manager(client, user_id, mgr["id"])
                logger.info("Manager impostato a: %s (id=%s)", args.manager, mgr["id"])
            else:
                logger.warning("Manager non trovato: %s", args.manager)

        # Aggiorna mailboxSettings (potrebbe fallire se non supportato)
        mailbox_settings = {
            "timeZone": args.tz,
            "language": {"locale": args.lang, "displayName": args.lang},
            "automaticRepliesSetting": {"status": "disabled"}
        }
        try:
            update_mailbox_settings(client, user_id, mailbox_settings)
            logger.info("mailboxSettings aggiornati")
        except Exception as e:
            logger.warning("Impossibile aggiornare mailboxSettings via Graph SDK: %s", e)

        # Aggiungi ai gruppi richiesti
        if args.groups:
            for g in args.groups:
                grp = find_group_by_display_name(client, g)
                if not grp:
                    logger.warning("Gruppo non trovato: %s", g)
                    continue
                try:
                    add_user_to_group(client, user_id, grp["id"])
                    logger.info("Aggiunto al gruppo: %s", g)
                except Exception as e:
                    logger.warning("Errore aggiunta gruppo %s: %s", g, e)

        summary = {
            "success": True,
            "user": args.user,
            "userId": user_id,
            "updatedAttributes": patch,
            "groupsRequested": args.groups,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    except Exception as exc:
        logger.exception("Errore durante l'onboarding con Graph SDK")
        print(json.dumps({"success": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
