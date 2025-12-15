#!/usr/bin/env python3
"""
Script Python per creare un gruppo di distribuzione su Exchange Online
Requisiti:
    pip install msal requests
    
Nota: Questo script usa Microsoft Graph API per creare un gruppo Microsoft 365
Per gruppi di distribuzione puri, è consigliato usare PowerShell
"""

import requests
import json
from typing import List, Dict, Any
import msal

# Configurazione Azure AD App
# È necessario registrare un'app in Azure AD con le seguenti permessi:
# - Group.ReadWrite.All
# - User.Read.All
CLIENT_ID = "your-client-id-here"
CLIENT_SECRET = "your-client-secret-here"
TENANT_ID = "your-tenant-id-here"

# Configurazione del gruppo
GROUP_CONFIG = {
    "displayName": "Marketing Team",
    "mailNickname": "marketing-team",
    "description": "Gruppo di distribuzione per il team Marketing",
    "mailEnabled": True,
    "securityEnabled": False,
    "groupTypes": []  # Array vuoto per gruppo di distribuzione
}

# Membri da aggiungere (User Principal Names)
MEMBERS = [
    "user1@contoso.com",
    "user2@contoso.com",
    "user3@contoso.com"
]


class ExchangeGroupManager:
    """Classe per gestire gruppi su Exchange Online tramite Microsoft Graph API"""
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
    def authenticate(self) -> bool:
        """Autentica con Microsoft Graph API"""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            print("✓ Autenticazione completata con successo")
            return True
        else:
            print(f"✗ Errore di autenticazione: {result.get('error_description')}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Restituisce gli headers per le richieste API"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def create_distribution_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuovo gruppo di distribuzione"""
        print("\n📧 Creazione del gruppo di distribuzione...")
        
        url = f"{self.graph_endpoint}/groups"
        response = requests.post(url, headers=self.get_headers(), json=config)
        
        if response.status_code == 201:
            group = response.json()
            print(f"✓ Gruppo creato con successo: {group['displayName']}")
            print(f"  ID: {group['id']}")
            print(f"  Email: {group.get('mail', 'N/A')}")
            return group
        else:
            print(f"✗ Errore nella creazione del gruppo: {response.status_code}")
            print(f"  {response.text}")
            return None
    
    def get_user_id(self, user_principal_name: str) -> str:
        """Ottiene l'ID di un utente dal suo UPN"""
        url = f"{self.graph_endpoint}/users/{user_principal_name}"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()["id"]
        return None
    
    def add_members_to_group(self, group_id: str, members: List[str]) -> None:
        """Aggiunge membri al gruppo"""
        print("\n👥 Aggiunta membri al gruppo...")
        
        for member_upn in members:
            try:
                user_id = self.get_user_id(member_upn)
                if not user_id:
                    print(f"  ✗ Utente non trovato: {member_upn}")
                    continue
                
                url = f"{self.graph_endpoint}/groups/{group_id}/members/$ref"
                data = {
                    "@odata.id": f"{self.graph_endpoint}/directoryObjects/{user_id}"
                }
                
                response = requests.post(url, headers=self.get_headers(), json=data)
                
                if response.status_code == 204:
                    print(f"  ✓ Aggiunto: {member_upn}")
                else:
                    print(f"  ✗ Errore nell'aggiungere {member_upn}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ Errore con {member_upn}: {str(e)}")
    
    def get_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """Ottiene i membri del gruppo"""
        url = f"{self.graph_endpoint}/groups/{group_id}/members"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json().get("value", [])
        return []
    
    def display_group_info(self, group_id: str) -> None:
        """Visualizza informazioni sul gruppo"""
        print("\n📋 Informazioni del gruppo:")
        
        # Informazioni base del gruppo
        url = f"{self.graph_endpoint}/groups/{group_id}"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            group = response.json()
            print(f"  Nome: {group['displayName']}")
            print(f"  Email: {group.get('mail', 'N/A')}")
            print(f"  Descrizione: {group.get('description', 'N/A')}")
        
        # Membri del gruppo
        members = self.get_group_members(group_id)
        print(f"\n👥 Membri del gruppo ({len(members)}):")
        for member in members:
            print(f"  - {member.get('displayName')} ({member.get('userPrincipalName', 'N/A')})")


def main():
    """Funzione principale"""
    print("=" * 60)
    print("Script per la creazione di gruppi su Exchange Online")
    print("=" * 60)
    
    # Verifica configurazione
    if CLIENT_ID == "your-client-id-here":
        print("\n⚠️  ATTENZIONE: Configurare CLIENT_ID, CLIENT_SECRET e TENANT_ID")
        print("Registrare un'app in Azure AD con i permessi:")
        print("  - Group.ReadWrite.All")
        print("  - User.Read.All")
        return
    
    # Inizializzazione manager
    manager = ExchangeGroupManager(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Autenticazione
    if not manager.authenticate():
        return
    
    # Creazione gruppo
    group = manager.create_distribution_group(GROUP_CONFIG)
    if not group:
        return
    
    # Aggiunta membri
    if MEMBERS:
        manager.add_members_to_group(group["id"], MEMBERS)
    
    # Visualizzazione informazioni finali
    manager.display_group_info(group["id"])
    
    print("\n✓ Operazione completata con successo!")


if __name__ == "__main__":
    main()
