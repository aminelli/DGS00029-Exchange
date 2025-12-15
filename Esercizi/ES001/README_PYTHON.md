# Exchange Online Transport Rule Manager - Python

Script Python per gestire Transport Rules e Outbound Connectors in Exchange Online tramite REST API.

## 📋 Prerequisiti

### 1. Registrazione App in Azure AD

Prima di utilizzare lo script, è necessario registrare un'applicazione in Azure AD:

#### Tramite Azure Portal:

1. Accedi al [Azure Portal](https://portal.azure.com)
2. Vai su **Azure Active Directory** > **App registrations**
3. Clicca su **New registration**
4. Inserisci:
   - **Name**: `Exchange-Transport-Manager`
   - **Supported account types**: `Accounts in this organizational directory only`
5. Clicca su **Register**

#### Configurazione API Permissions:

1. Vai su **API permissions** nella tua app
2. Clicca su **Add a permission**
3. Seleziona **APIs my organization uses**
4. Cerca `Office 365 Exchange Online` o `Outlook`
5. Seleziona **Application permissions**
6. Aggiungi: `Exchange.ManageAsApp`
7. Clicca su **Grant admin consent**

#### Creazione Client Secret:

1. Vai su **Certificates & secrets**
2. Clicca su **New client secret**
3. Inserisci una descrizione e seleziona la scadenza
4. **COPIA IL SECRET** (non sarà più visibile dopo)

### 2. Installazione Python

Assicurati di avere Python 3.8 o superiore installato:

```bash
python --version
```

### 3. Installazione Dipendenze

```bash
# Naviga nella directory dello script
cd "d:\Corsi\Library\Code\Products\MSExchange\CORSI\DGS00029-Exchange\github\Esercizi\ES001"

# Installa le dipendenze
pip install -r requirements.txt
```

## 🚀 Utilizzo

### Metodo 1: Configurazione diretta nello script

1. Apri il file `exchange_transport_rule_manager.py`
2. Modifica le variabili di configurazione nella sezione `CONFIGURAZIONE`:

```python
TENANT_ID = "12345678-1234-1234-1234-123456789abc"
CLIENT_ID = "abcdefgh-abcd-abcd-abcd-abcdefghijkl"
CLIENT_SECRET = "your-secret-value-here"

OUTBOUND_CONNECTOR_NAME = "ConnettoreOutbound-Partner"
SMART_HOST = "mail.partner-domain.com"

TRANSPORT_RULE_NAME = "Instrada-Email-Partner"
DESTINATION_DOMAIN = "partner-domain.com"
RULE_PRIORITY = 0
```

3. Esegui lo script:

```bash
python exchange_transport_rule_manager.py
```

### Metodo 2: Uso del file di configurazione

1. Copia `config_example.json` in `config.json`
2. Modifica `config.json` con le tue credenziali
3. Modifica lo script per caricare la configurazione dal file JSON

## 📊 Output dello Script

Lo script fornisce output dettagliato durante l'esecuzione:

```
============================================================
🚀 EXCHANGE ONLINE TRANSPORT RULE MANAGER
============================================================
🔐 Ottenimento token di accesso...
✓ Token ottenuto con successo
  Scadenza: 2025-12-15 14:30:00

------------------------------------------------------------
STEP 1: Gestione Outbound Connector
------------------------------------------------------------

📋 Recupero lista Outbound Connectors...
✓ Trovati 3 connettori

🔧 Creazione Outbound Connector: ConnettoreOutbound-DominioSpecifico
✓ Connettore creato con successo
  Nome: ConnettoreOutbound-DominioSpecifico
  SmartHosts: ['mail.example-partner.com']
  Abilitato: True

------------------------------------------------------------
STEP 2: Gestione Transport Rule
------------------------------------------------------------

📋 Recupero lista Transport Rules...
✓ Trovate 8 regole

📜 Creazione Transport Rule: Instrada-Email-Dominio-Specifico
✓ Regola creata con successo
  Nome: Instrada-Email-Dominio-Specifico
  Priorità: 0
  Stato: Enabled

============================================================
📊 RIEPILOGO CONFIGURAZIONE
============================================================

🔧 CONNETTORE OUTBOUND:
  Nome: ConnettoreOutbound-DominioSpecifico
  SmartHosts: mail.example-partner.com
  Abilitato: True
  TLS Settings: DomainValidation
  ID: 12345678-abcd-1234-abcd-123456789abc

📜 REGOLA DI TRASPORTO:
  Nome: Instrada-Email-Dominio-Specifico
  Priorità: 0
  Dominio destinazione: example-partner.com
  Connettore usato: ConnettoreOutbound-DominioSpecifico
  Stato: Enabled
  ID: 87654321-dcba-4321-dcba-987654321abc

============================================================

✅ Configurazione completata con successo!
   Tutte le email dirette a @example-partner.com
   saranno instradate attraverso il connettore 'ConnettoreOutbound-DominioSpecifico'
```

## 🔧 Struttura dei File

```
ES001/
├── exchange_transport_rule_manager.py  # Script principale
├── requirements.txt                    # Dipendenze Python
├── config_example.json                 # Esempio configurazione
├── README_PYTHON.md                    # Questa guida
└── MSGraph-TransportRules-Python.md   # Documentazione API
```

## 📚 Classi Disponibili

### ExchangeOnlineClient
Classe base per l'autenticazione e la gestione dei token.

```python
client = ExchangeOnlineClient(tenant_id, client_id, client_secret)
token = client.get_access_token()
```

### OutboundConnectorManager
Gestione completa degli Outbound Connectors.

```python
connector_mgr = OutboundConnectorManager(tenant_id, client_id, client_secret)

# Lista connettori
connectors = connector_mgr.list_outbound_connectors()

# Ottieni connettore specifico
connector = connector_mgr.get_outbound_connector("nome-connettore")

# Crea nuovo connettore
new_connector = connector_mgr.create_outbound_connector({
    "Name": "MioConnettore",
    "SmartHosts": ["mail.example.com"],
    "Enabled": True
})

# Aggiorna connettore
updated = connector_mgr.update_outbound_connector(connector_id, data)

# Elimina connettore
connector_mgr.delete_outbound_connector(connector_id)
```

### TransportRuleManager
Gestione completa delle Transport Rules.

```python
rule_mgr = TransportRuleManager(tenant_id, client_id, client_secret)

# Lista regole
rules = rule_mgr.list_transport_rules()

# Ottieni regola specifica
rule = rule_mgr.get_transport_rule("nome-regola")

# Crea nuova regola
new_rule = rule_mgr.create_transport_rule({
    "Name": "MiaRegola",
    "RecipientDomainIs": ["example.com"],
    "RouteMessageOutboundConnector": "MioConnettore",
    "Priority": 0
})

# Aggiorna regola
updated = rule_mgr.update_transport_rule(rule_id, data)

# Elimina regola
rule_mgr.delete_transport_rule(rule_id)
```

## 🔍 Troubleshooting

### Errore di autenticazione

```
✗ Errore nell'ottenimento del token: AADSTS700016
```

**Soluzione:** Verifica che l'app abbia il permesso `Exchange.ManageAsApp` e che sia stato dato il consenso admin.

### Errore 401 Unauthorized

```
Errore 401: Unauthorized
```

**Soluzione:** Il token potrebbe essere scaduto o non valido. Verifica:
- Client ID corretto
- Client Secret valido e non scaduto
- Permessi corretti assegnati

### Errore 404 Not Found

```
Errore 404: Not Found
```

**Soluzione:** Verifica che l'endpoint API sia corretto e che la risorsa esista.

### Connettore o regola già esistente

Lo script gestisce automaticamente questa situazione chiedendo conferma per ricreare la risorsa.

## ⚙️ Personalizzazione

### Modifica configurazione TLS

```python
connector_data = {
    "Name": "MioConnettore",
    "SmartHosts": ["mail.example.com"],
    "TlsSettings": "EncryptionOnly",  # DomainValidation, EncryptionOnly, CertificateValidation
    "Enabled": True
}
```

### Aggiunta condizioni alla Transport Rule

```python
rule_data = {
    "Name": "RegolaComplessa",
    "RecipientDomainIs": ["example.com"],
    "SenderDomainIs": ["mycompany.com"],  # Aggiungi condizione dominio mittente
    "SubjectContainsWords": ["urgent"],   # Aggiungi condizione oggetto
    "RouteMessageOutboundConnector": "MioConnettore",
    "Priority": 0
}
```

## 🆚 Confronto con PowerShell

| Caratteristica | Python | PowerShell |
|----------------|--------|------------|
| Setup iniziale | Più complesso | Più semplice |
| Integrazione CI/CD | Eccellente | Buona |
| Gestione errori | Personalizzabile | Standard |
| Cross-platform | ✅ Sì | ⚠️ PowerShell Core |
| Documentazione | Limitata | Ottima |
| Facilità d'uso | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📖 Riferimenti

- [Azure Identity Python SDK](https://docs.microsoft.com/en-us/python/api/azure-identity)
- [Exchange Online PowerShell](https://docs.microsoft.com/en-us/powershell/exchange/exchange-online-powershell)
- [Azure AD App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

## 📝 Note

- Le REST API di Exchange Online non sono completamente documentate pubblicamente
- Alcuni endpoint potrebbero cambiare senza preavviso
- Per operazioni semplici, PowerShell rimane la scelta consigliata
- Usa Python quando hai bisogno di integrazione con sistemi esistenti

## 🤝 Supporto

Per problemi o domande:
1. Verifica la documentazione ufficiale Microsoft
2. Controlla i log di errore dettagliati
3. Assicurati che i permessi Azure AD siano corretti
