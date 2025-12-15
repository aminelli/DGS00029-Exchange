"""
Exchange Online Transport Rule Manager
Script per creare Transport Rules e Outbound Connectors tramite Exchange Online REST API

Autore: Exchange Admin
Data: 15/12/2025
Requisiti: azure-identity, requests
"""

import requests
import json
import sys
from typing import Dict, List, Optional
from azure.identity import ClientSecretCredential
from datetime import datetime


class ExchangeOnlineClient:
    """Client base per interagire con Exchange Online REST API"""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Inizializza il client Exchange Online
        
        Args:
            tenant_id: ID del tenant Azure AD
            client_id: ID dell'applicazione registrata
            client_secret: Secret dell'applicazione
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://outlook.office365.com/adminapi/beta"
        self.token = None
        self.token_expiry = None
    
    def get_access_token(self) -> str:
        """
        Ottiene il token di accesso per Exchange Online
        
        Returns:
            Token di accesso come stringa
        """
        print("🔐 Ottenimento token di accesso...")
        
        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # Scope per Exchange Online
            scope = "https://outlook.office365.com/.default"
            token = credential.get_token(scope)
            self.token = token.token
            self.token_expiry = datetime.fromtimestamp(token.expires_on)
            
            print("✓ Token ottenuto con successo")
            print(f"  Scadenza: {self.token_expiry}")
            
            return self.token
            
        except Exception as e:
            print(f"✗ Errore nell'ottenimento del token: {str(e)}")
            raise
    
    def get_headers(self) -> Dict[str, str]:
        """
        Prepara gli headers per le richieste API
        
        Returns:
            Dictionary con gli headers HTTP
        """
        if not self.token:
            self.get_access_token()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }


class OutboundConnectorManager(ExchangeOnlineClient):
    """Manager per la gestione degli Outbound Connectors"""
    
    def list_outbound_connectors(self) -> List[Dict]:
        """
        Elenca tutti gli Outbound Connectors
        
        Returns:
            Lista di connettori outbound
        """
        print("\n📋 Recupero lista Outbound Connectors...")
        
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            connectors = response.json().get('value', [])
            print(f"✓ Trovati {len(connectors)} connettori")
            return connectors
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def get_outbound_connector(self, connector_name: str) -> Optional[Dict]:
        """
        Ottiene i dettagli di un Outbound Connector specifico
        
        Args:
            connector_name: Nome del connettore
            
        Returns:
            Dettagli del connettore o None se non trovato
        """
        connectors = self.list_outbound_connectors()
        
        for connector in connectors:
            if connector.get('Name') == connector_name:
                return connector
        
        return None
    
    def create_outbound_connector(self, connector_data: Dict) -> Dict:
        """
        Crea un nuovo Outbound Connector
        
        Args:
            connector_data: Dati di configurazione del connettore
            
        Returns:
            Dettagli del connettore creato
        """
        print(f"\n🔧 Creazione Outbound Connector: {connector_data.get('Name')}")
        
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector"
        
        response = requests.post(
            url,
            headers=self.get_headers(),
            data=json.dumps(connector_data)
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ Connettore creato con successo")
            print(f"  Nome: {result.get('Name')}")
            print(f"  SmartHosts: {result.get('SmartHosts')}")
            print(f"  Abilitato: {result.get('Enabled')}")
            return result
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def update_outbound_connector(self, connector_id: str, connector_data: Dict) -> Dict:
        """
        Aggiorna un Outbound Connector esistente
        
        Args:
            connector_id: ID del connettore da aggiornare
            connector_data: Nuovi dati di configurazione
            
        Returns:
            Dettagli del connettore aggiornato
        """
        print(f"\n🔄 Aggiornamento Outbound Connector: {connector_id}")
        
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector('{connector_id}')"
        
        response = requests.patch(
            url,
            headers=self.get_headers(),
            data=json.dumps(connector_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Connettore aggiornato con successo")
            return result
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def delete_outbound_connector(self, connector_id: str) -> bool:
        """
        Elimina un Outbound Connector
        
        Args:
            connector_id: ID del connettore da eliminare
            
        Returns:
            True se eliminato con successo
        """
        print(f"\n🗑️  Eliminazione Outbound Connector: {connector_id}")
        
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector('{connector_id}')"
        response = requests.delete(url, headers=self.get_headers())
        
        if response.status_code == 204:
            print(f"✓ Connettore eliminato con successo")
            return True
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")


class TransportRuleManager(ExchangeOnlineClient):
    """Manager per la gestione delle Transport Rules"""
    
    def list_transport_rules(self) -> List[Dict]:
        """
        Elenca tutte le Transport Rules
        
        Returns:
            Lista di regole di trasporto
        """
        print("\n📋 Recupero lista Transport Rules...")
        
        url = f"{self.base_url}/{self.tenant_id}/TransportRule"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            rules = response.json().get('value', [])
            print(f"✓ Trovate {len(rules)} regole")
            return rules
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def get_transport_rule(self, rule_name: str) -> Optional[Dict]:
        """
        Ottiene i dettagli di una Transport Rule specifica
        
        Args:
            rule_name: Nome della regola
            
        Returns:
            Dettagli della regola o None se non trovata
        """
        rules = self.list_transport_rules()
        
        for rule in rules:
            if rule.get('Name') == rule_name:
                return rule
        
        return None
    
    def create_transport_rule(self, rule_data: Dict) -> Dict:
        """
        Crea una nuova Transport Rule
        
        Args:
            rule_data: Dati di configurazione della regola
            
        Returns:
            Dettagli della regola creata
        """
        print(f"\n📜 Creazione Transport Rule: {rule_data.get('Name')}")
        
        url = f"{self.base_url}/{self.tenant_id}/TransportRule"
        
        response = requests.post(
            url,
            headers=self.get_headers(),
            data=json.dumps(rule_data)
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ Regola creata con successo")
            print(f"  Nome: {result.get('Name')}")
            print(f"  Priorità: {result.get('Priority')}")
            print(f"  Stato: {result.get('State')}")
            return result
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def update_transport_rule(self, rule_id: str, rule_data: Dict) -> Dict:
        """
        Aggiorna una Transport Rule esistente
        
        Args:
            rule_id: ID della regola da aggiornare
            rule_data: Nuovi dati di configurazione
            
        Returns:
            Dettagli della regola aggiornata
        """
        print(f"\n🔄 Aggiornamento Transport Rule: {rule_id}")
        
        url = f"{self.base_url}/{self.tenant_id}/TransportRule('{rule_id}')"
        
        response = requests.patch(
            url,
            headers=self.get_headers(),
            data=json.dumps(rule_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Regola aggiornata con successo")
            return result
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")
    
    def delete_transport_rule(self, rule_id: str) -> bool:
        """
        Elimina una Transport Rule
        
        Args:
            rule_id: ID della regola da eliminare
            
        Returns:
            True se eliminata con successo
        """
        print(f"\n🗑️  Eliminazione Transport Rule: {rule_id}")
        
        url = f"{self.base_url}/{self.tenant_id}/TransportRule('{rule_id}')"
        response = requests.delete(url, headers=self.get_headers())
        
        if response.status_code == 204:
            print(f"✓ Regola eliminata con successo")
            return True
        else:
            raise Exception(f"Errore {response.status_code}: {response.text}")


def print_configuration_summary(connector: Dict, rule: Dict):
    """
    Visualizza il riepilogo della configurazione
    
    Args:
        connector: Dati del connettore
        rule: Dati della regola
    """
    print("\n" + "="*60)
    print("📊 RIEPILOGO CONFIGURAZIONE")
    print("="*60)
    
    print("\n🔧 CONNETTORE OUTBOUND:")
    print(f"  Nome: {connector.get('Name')}")
    print(f"  SmartHosts: {', '.join(connector.get('SmartHosts', []))}")
    print(f"  Abilitato: {connector.get('Enabled')}")
    print(f"  TLS Settings: {connector.get('TlsSettings')}")
    print(f"  ID: {connector.get('Identity')}")
    
    print("\n📜 REGOLA DI TRASPORTO:")
    print(f"  Nome: {rule.get('Name')}")
    print(f"  Priorità: {rule.get('Priority')}")
    print(f"  Dominio destinazione: {', '.join(rule.get('RecipientDomainIs', []))}")
    print(f"  Connettore usato: {rule.get('RouteMessageOutboundConnector')}")
    print(f"  Stato: {rule.get('State')}")
    print(f"  ID: {rule.get('Identity')}")
    
    print("\n" + "="*60)


def main():
    """Funzione principale dello script"""
    
    print("="*60)
    print("🚀 EXCHANGE ONLINE TRANSPORT RULE MANAGER")
    print("="*60)
    
    # ==========================================
    # CONFIGURAZIONE - MODIFICA QUESTI VALORI
    # ==========================================
    
    TENANT_ID = "your-tenant-id-here"
    CLIENT_ID = "your-client-id-here"
    CLIENT_SECRET = "your-client-secret-here"
    
    # Configurazione Outbound Connector
    OUTBOUND_CONNECTOR_NAME = "ConnettoreOutbound-DominioSpecifico"
    SMART_HOST = "mail.example-partner.com"
    
    # Configurazione Transport Rule
    TRANSPORT_RULE_NAME = "Instrada-Email-Dominio-Specifico"
    DESTINATION_DOMAIN = "example-partner.com"
    RULE_PRIORITY = 0
    
    # ==========================================
    
    # Verifica che le credenziali siano state configurate
    if "your-" in TENANT_ID or "your-" in CLIENT_ID or "your-" in CLIENT_SECRET:
        print("\n⚠️  ATTENZIONE: Configura le credenziali Azure AD nello script!")
        print("   Modifica le variabili TENANT_ID, CLIENT_ID e CLIENT_SECRET")
        sys.exit(1)
    
    try:
        # Inizializza i manager
        connector_mgr = OutboundConnectorManager(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        rule_mgr = TransportRuleManager(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        
        # ==========================================
        # STEP 1: Gestione Outbound Connector
        # ==========================================
        
        print("\n" + "-"*60)
        print("STEP 1: Gestione Outbound Connector")
        print("-"*60)
        
        # Verifica se il connettore esiste già
        existing_connector = connector_mgr.get_outbound_connector(OUTBOUND_CONNECTOR_NAME)
        
        if existing_connector:
            print(f"\n⚠️  Connettore '{OUTBOUND_CONNECTOR_NAME}' già esistente")
            print(f"   ID: {existing_connector.get('Identity')}")
            
            response = input("\nVuoi ricrearlo? (s/n): ").lower()
            if response == 's':
                connector_mgr.delete_outbound_connector(existing_connector.get('Identity'))
                existing_connector = None
        
        if not existing_connector:
            # Crea il connettore
            connector_data = {
                "Name": OUTBOUND_CONNECTOR_NAME,
                "Enabled": True,
                "UseMXRecord": False,
                "SmartHosts": [SMART_HOST],
                "TlsSettings": "DomainValidation",
                "CloudServicesMailEnabled": False,
                "Comment": f"Connettore per instradare email verso {SMART_HOST}"
            }
            
            connector = connector_mgr.create_outbound_connector(connector_data)
        else:
            connector = existing_connector
        
        # ==========================================
        # STEP 2: Gestione Transport Rule
        # ==========================================
        
        print("\n" + "-"*60)
        print("STEP 2: Gestione Transport Rule")
        print("-"*60)
        
        # Verifica se la regola esiste già
        existing_rule = rule_mgr.get_transport_rule(TRANSPORT_RULE_NAME)
        
        if existing_rule:
            print(f"\n⚠️  Regola '{TRANSPORT_RULE_NAME}' già esistente")
            print(f"   ID: {existing_rule.get('Identity')}")
            
            response = input("\nVuoi ricrearla? (s/n): ").lower()
            if response == 's':
                rule_mgr.delete_transport_rule(existing_rule.get('Identity'))
                existing_rule = None
        
        if not existing_rule:
            # Crea la regola
            rule_data = {
                "Name": TRANSPORT_RULE_NAME,
                "Priority": RULE_PRIORITY,
                "State": "Enabled",
                "RecipientDomainIs": [DESTINATION_DOMAIN],
                "RouteMessageOutboundConnector": OUTBOUND_CONNECTOR_NAME,
                "Comments": f"Instrada email verso {DESTINATION_DOMAIN} tramite connettore {OUTBOUND_CONNECTOR_NAME}"
            }
            
            rule = rule_mgr.create_transport_rule(rule_data)
        else:
            rule = existing_rule
        
        # ==========================================
        # STEP 3: Riepilogo configurazione
        # ==========================================
        
        print_configuration_summary(connector, rule)
        
        print("\n✅ Configurazione completata con successo!")
        print(f"   Tutte le email dirette a @{DESTINATION_DOMAIN}")
        print(f"   saranno instradate attraverso il connettore '{OUTBOUND_CONNECTOR_NAME}'")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
