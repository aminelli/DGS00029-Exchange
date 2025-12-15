# Microsoft Graph API per Transport Rules e Connettori Outbound

## Panoramica

**Importante:** Le **Transport Rules** e i **Connettori Outbound** di Exchange Online **non sono attualmente disponibili tramite Microsoft Graph API**. Queste funzionalità sono gestibili esclusivamente tramite:

1. **Exchange Online PowerShell** (metodo principale)
2. **Exchange Online REST API** (non Microsoft Graph)
3. **Exchange Web Services (EWS)** (legacy, non raccomandato)

## Limitazioni di Microsoft Graph

Microsoft Graph API non espone endpoint per:
- ❌ Transport Rules (regole di trasporto)
- ❌ Outbound Connectors (connettori outbound)
- ❌ Inbound Connectors (connettori inbound)
- ❌ Mail flow configurations avanzate

## Alternative con Microsoft Graph

### 1. Gestione delle Mail tramite Rules (Regole Inbox utente)

Sebbene non sia equivalente alle Transport Rules a livello organizzativo, è possibile gestire **regole inbox degli utenti** con Microsoft Graph:

```python
from msgraph import GraphServiceClient
from msgraph.generated.models.message_rule import MessageRule
from msgraph.generated.models.message_rule_actions import MessageRuleActions
from msgraph.generated.models.message_rule_predicates import MessageRulePredicates
from azure.identity import ClientSecretCredential

# Configurazione autenticazione
tenant_id = "your-tenant-id"
client_id = "your-client-id"
client_secret = "your-client-secret"

credential = ClientSecretCredential(tenant_id, client_id, client_secret)
scopes = ['https://graph.microsoft.com/.default']

# Inizializza il client
client = GraphServiceClient(credentials=credential, scopes=scopes)

# Crea una regola per un utente specifico
async def create_user_inbox_rule(user_id: str):
    """
    Crea una regola inbox per un utente (NON equivalente a Transport Rule)
    """
    rule = MessageRule()
    rule.display_name = "Inoltra email a dominio specifico"
    rule.sequence = 1
    rule.is_enabled = True
    
    # Condizioni
    conditions = MessageRulePredicates()
    conditions.recipient_contains = ["@example-partner.com"]
    rule.conditions = conditions
    
    # Azioni
    actions = MessageRuleActions()
    actions.forward_to = [{"emailAddress": {"address": "forwarder@example.com"}}]
    rule.actions = actions
    
    result = await client.users.by_user_id(user_id).mail_folders.by_mail_folder_id('inbox').message_rules.post(rule)
    return result

# Endpoint: POST /users/{id}/mailFolders/inbox/messageRules
```

**Limitazioni:** Questa è una regola a livello utente, non organizzativo.

### 2. Monitoraggio dei Messaggi (Mail Reports)

È possibile monitorare il flusso di posta tramite Microsoft Graph Reports API:

```python
async def get_email_activity_report():
    """
    Ottiene report sull'attività email
    """
    # Endpoint: GET /reports/getEmailActivityUserDetail(period='D7')
    report = await client.reports.get_email_activity_user_detail(period='D7').get()
    return report

async def get_email_app_usage():
    """
    Ottiene report sull'utilizzo delle app email
    """
    # Endpoint: GET /reports/getEmailAppUsageUserDetail(period='D7')
    report = await client.reports.get_email_app_usage_user_detail(period='D7').get()
    return report
```

## Soluzione: Exchange Online REST API con Python

Per gestire Transport Rules e Connettori, è necessario usare **Exchange Online REST API** direttamente:

### Configurazione

```python
import requests
from azure.identity import ClientSecretCredential
import json

class ExchangeOnlineClient:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://outlook.office365.com/adminapi/beta"
        self.token = None
    
    def get_access_token(self):
        """
        Ottiene il token di accesso per Exchange Online
        """
        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Scope per Exchange Online
        scope = "https://outlook.office365.com/.default"
        token = credential.get_token(scope)
        self.token = token.token
        return self.token
    
    def get_headers(self):
        """
        Prepara gli headers per le richieste
        """
        if not self.token:
            self.get_access_token()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
```

### Gestione Transport Rules

```python
class TransportRuleManager(ExchangeOnlineClient):
    
    def list_transport_rules(self):
        """
        Elenca tutte le Transport Rules
        Endpoint: GET /TransportRule
        """
        url = f"{self.base_url}/{self.tenant_id}/TransportRule"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def get_transport_rule(self, rule_id: str):
        """
        Ottiene i dettagli di una Transport Rule specifica
        Endpoint: GET /TransportRule/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/TransportRule('{rule_id}')"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def create_transport_rule(self, rule_data: dict):
        """
        Crea una nuova Transport Rule
        Endpoint: POST /TransportRule
        """
        url = f"{self.base_url}/{self.tenant_id}/TransportRule"
        
        response = requests.post(
            url, 
            headers=self.get_headers(),
            data=json.dumps(rule_data)
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def update_transport_rule(self, rule_id: str, rule_data: dict):
        """
        Aggiorna una Transport Rule esistente
        Endpoint: PATCH /TransportRule/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/TransportRule('{rule_id}')"
        
        response = requests.patch(
            url,
            headers=self.get_headers(),
            data=json.dumps(rule_data)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def delete_transport_rule(self, rule_id: str):
        """
        Elimina una Transport Rule
        Endpoint: DELETE /TransportRule/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/TransportRule('{rule_id}')"
        response = requests.delete(url, headers=self.get_headers())
        
        if response.status_code == 204:
            return True
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
```

### Gestione Outbound Connectors

```python
class OutboundConnectorManager(ExchangeOnlineClient):
    
    def list_outbound_connectors(self):
        """
        Elenca tutti gli Outbound Connectors
        Endpoint: GET /OutboundConnector
        """
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def get_outbound_connector(self, connector_id: str):
        """
        Ottiene i dettagli di un Outbound Connector specifico
        Endpoint: GET /OutboundConnector/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector('{connector_id}')"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def create_outbound_connector(self, connector_data: dict):
        """
        Crea un nuovo Outbound Connector
        Endpoint: POST /OutboundConnector
        """
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector"
        
        response = requests.post(
            url,
            headers=self.get_headers(),
            data=json.dumps(connector_data)
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def update_outbound_connector(self, connector_id: str, connector_data: dict):
        """
        Aggiorna un Outbound Connector esistente
        Endpoint: PATCH /OutboundConnector/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector('{connector_id}')"
        
        response = requests.patch(
            url,
            headers=self.get_headers(),
            data=json.dumps(connector_data)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
    
    def delete_outbound_connector(self, connector_id: str):
        """
        Elimina un Outbound Connector
        Endpoint: DELETE /OutboundConnector/{id}
        """
        url = f"{self.base_url}/{self.tenant_id}/OutboundConnector('{connector_id}')"
        response = requests.delete(url, headers=self.get_headers())
        
        if response.status_code == 204:
            return True
        else:
            raise Exception(f"Errore: {response.status_code} - {response.text}")
```

## Esempio Completo di Utilizzo

```python
import asyncio

async def main():
    # Configurazione
    tenant_id = "your-tenant-id"
    client_id = "your-app-id"
    client_secret = "your-secret"
    
    # Inizializza i manager
    connector_mgr = OutboundConnectorManager(tenant_id, client_id, client_secret)
    rule_mgr = TransportRuleManager(tenant_id, client_id, client_secret)
    
    try:
        # 1. Crea l'Outbound Connector
        connector_data = {
            "Name": "ConnettoreOutbound-DominioSpecifico",
            "Enabled": True,
            "UseMXRecord": False,
            "SmartHosts": ["mail.example-partner.com"],
            "TlsSettings": "DomainValidation",
            "CloudServicesMailEnabled": False,
            "Comment": "Connettore per instradare email verso dominio partner"
        }
        
        print("Creazione Outbound Connector...")
        connector = connector_mgr.create_outbound_connector(connector_data)
        print(f"✓ Connettore creato: {connector['Name']}")
        
        # 2. Crea la Transport Rule
        rule_data = {
            "Name": "Instrada-Email-Dominio-Specifico",
            "Priority": 0,
            "State": "Enabled",
            "RecipientDomainIs": ["example-partner.com"],
            "RouteMessageOutboundConnector": "ConnettoreOutbound-DominioSpecifico",
            "Comments": "Instrada email verso dominio partner tramite connettore dedicato"
        }
        
        print("Creazione Transport Rule...")
        rule = rule_mgr.create_transport_rule(rule_data)
        print(f"✓ Regola creata: {rule['Name']}")
        
        # 3. Verifica configurazione
        print("\n--- RIEPILOGO CONFIGURAZIONE ---")
        print(f"Connettore: {connector['Name']}")
        print(f"SmartHosts: {connector['SmartHosts']}")
        print(f"\nRegola: {rule['Name']}")
        print(f"Dominio destinazione: {rule['RecipientDomainIs']}")
        print(f"Connettore usato: {rule['RouteMessageOutboundConnector']}")
        
    except Exception as e:
        print(f"✗ Errore: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Registrazione App in Azure AD

Per utilizzare le API, è necessario registrare un'applicazione in Azure AD:

### 1. Registrazione App

```bash
# Tramite Azure CLI
az ad app create \
    --display-name "Exchange-Transport-Manager" \
    --sign-in-audience AzureADMyOrg
```

### 2. Permessi Richiesti

**API Permissions necessari:**

- **Exchange Online:**
  - `Exchange.ManageAsApp` (Application permission)
  
**Microsoft Graph (per funzionalità aggiuntive):**
  - `Mail.ReadWrite` (per regole inbox utente)
  - `MailboxSettings.ReadWrite` (per impostazioni mailbox)
  - `User.Read.All` (per accedere agli utenti)

### 3. Configurazione nel codice

```python
# requirements.txt
azure-identity==1.15.0
msgraph-sdk==1.3.0
requests==2.31.0
```

```python
# Installazione dipendenze
# pip install -r requirements.txt
```

## Confronto: PowerShell vs REST API

| Funzionalità | PowerShell | REST API | Microsoft Graph |
|--------------|-----------|----------|-----------------|
| Transport Rules | ✅ Completo | ✅ Completo | ❌ Non disponibile |
| Outbound Connectors | ✅ Completo | ✅ Completo | ❌ Non disponibile |
| Inbound Connectors | ✅ Completo | ✅ Completo | ❌ Non disponibile |
| Facilità d'uso | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | N/A |
| Automazione CI/CD | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | N/A |
| Documentazione | Ottima | Limitata | N/A |

## Conclusioni

### Raccomandazioni

1. **Per script semplici e amministrazione:** Usa **PowerShell** (come nello script fornito)
2. **Per integrazione in applicazioni Python:** Usa **Exchange Online REST API** (esempi sopra)
3. **Per funzionalità a livello utente:** Usa **Microsoft Graph SDK** (regole inbox individuali)

### Limitazioni da considerare

- Le REST API di Exchange Online non sono completamente documentate pubblicamente
- Alcuni endpoint potrebbero cambiare senza preavviso
- La copertura di Microsoft Graph per Exchange Online è limitata alle operazioni base

### Link Utili

- [Microsoft Graph SDK for Python](https://github.com/microsoftgraph/msgraph-sdk-python)
- [Exchange Online PowerShell](https://docs.microsoft.com/en-us/powershell/exchange/exchange-online-powershell)
- [Microsoft Graph API Reference](https://docs.microsoft.com/en-us/graph/api/overview)
- [Azure Identity Python SDK](https://docs.microsoft.com/en-us/python/api/azure-identity)
