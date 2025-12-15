# Creazione Gruppi di Distribuzione su Exchange Online

Questo repository contiene script PowerShell e Python per creare gruppi di distribuzione su Exchange Online.

## 📁 File

- **New-ExchangeDistributionGroup.ps1** - Script PowerShell per Exchange Online
- **new_exchange_distribution_group.py** - Script Python con Microsoft Graph API

## 🔧 Prerequisiti

### PowerShell
```powershell
# Installare il modulo ExchangeOnlineManagement
Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber
```

### Python
```bash
# Installare le dipendenze
pip install msal requests
```

Per lo script Python, è necessario registrare un'applicazione in Azure AD:
1. Accedere al [portale Azure](https://portal.azure.com)
2. Andare su Azure Active Directory > App registrations > New registration
3. Assegnare i permessi API:
   - `Group.ReadWrite.All`
   - `User.Read.All`
4. Creare un client secret
5. Annotare: Client ID, Client Secret, Tenant ID

## 🚀 Utilizzo

### PowerShell
```powershell
# Modificare i parametri nello script
$GroupName = "Marketing Team"
$GroupEmail = "marketing@contoso.com"
$Members = @("user1@contoso.com", "user2@contoso.com")

# Eseguire lo script
.\New-ExchangeDistributionGroup.ps1
```

### Python
```python
# Configurare le credenziali nello script
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
TENANT_ID = "your-tenant-id"

# Eseguire lo script
python new_exchange_distribution_group.py
```

## 📝 Funzionalità

Entrambi gli script permettono di:
- ✅ Creare un nuovo gruppo di distribuzione
- ✅ Configurare nome, alias e descrizione
- ✅ Aggiungere membri al gruppo
- ✅ Visualizzare informazioni del gruppo
- ✅ Gestione errori

## ⚠️ Note

- **PowerShell**: Metodo raccomandato per gruppi di distribuzione puri su Exchange Online
- **Python**: Usa Microsoft Graph API, ideale per integrazioni con altre applicazioni
- Assicurarsi di avere i permessi necessari per creare gruppi nel tenant

## 📖 Riferimenti

- [Exchange Online PowerShell](https://docs.microsoft.com/powershell/exchange/exchange-online-powershell)
- [Microsoft Graph API - Groups](https://docs.microsoft.com/graph/api/resources/group)
