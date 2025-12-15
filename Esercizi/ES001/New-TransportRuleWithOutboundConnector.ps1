<#
.SYNOPSIS
    Script per creare una regola di trasporto in Exchange Online che usa un connettore outbound
    per instradare le email verso un dominio specifico.

.DESCRIPTION
    Questo script crea una Transport Rule in Exchange Online che veicola il traffico email
    verso un dominio specifico attraverso un connettore outbound definito.

.NOTES
    Autore: Exchange Admin
    Data: 15/12/2025
    Requisiti: Modulo ExchangeOnlineManagement
#>

# Parametri di configurazione
param(
    [Parameter(Mandatory=$false)]
    [string]$OutboundConnectorName = "ConnettoreOutbound-DominioSpecifico",
    
    [Parameter(Mandatory=$false)]
    [string]$TransportRuleName = "Instrada-Email-Dominio-Specifico",
    
    [Parameter(Mandatory=$false)]
    [string]$DominioDestinazione = "example-partner.com",
    
    [Parameter(Mandatory=$false)]
    [string]$SmartHost = "mail.example-partner.com",
    
    [Parameter(Mandatory=$false)]
    [int]$Priority = 0
)

# Funzione per verificare e installare il modulo Exchange Online
function Ensure-ExchangeOnlineModule {
    if (-not (Get-Module -ListAvailable -Name ExchangeOnlineManagement)) {
        Write-Host "Installazione del modulo ExchangeOnlineManagement..." -ForegroundColor Yellow
        Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber -Scope CurrentUser
    }
    Import-Module ExchangeOnlineManagement
}

# Funzione per connettersi a Exchange Online
function Connect-ToExchangeOnline {
    try {
        Write-Host "Connessione a Exchange Online..." -ForegroundColor Cyan
        Connect-ExchangeOnline -ShowBanner:$false
        Write-Host "Connessione riuscita!" -ForegroundColor Green
    }
    catch {
        Write-Error "Errore durante la connessione a Exchange Online: $_"
        exit 1
    }
}

# Funzione per creare o verificare il connettore outbound
function New-OutboundConnectorIfNotExists {
    param(
        [string]$ConnectorName,
        [string]$SmartHost
    )
    
    Write-Host "`nVerifica esistenza connettore outbound '$ConnectorName'..." -ForegroundColor Cyan
    
    $existingConnector = Get-OutboundConnector -Identity $ConnectorName -ErrorAction SilentlyContinue
    
    if ($existingConnector) {
        Write-Host "Connettore outbound '$ConnectorName' già esistente." -ForegroundColor Yellow
        Write-Host "SmartHosts configurati: $($existingConnector.SmartHosts -join ', ')" -ForegroundColor Gray
        return $existingConnector
    }
    else {
        Write-Host "Creazione del connettore outbound '$ConnectorName'..." -ForegroundColor Cyan
        
        try {
            $connector = New-OutboundConnector `
                -Name $ConnectorName `
                -Enabled $true `
                -UseMxRecord $false `
                -SmartHosts $SmartHost `
                -TlsSettings DomainValidation `
                -CloudServicesMailEnabled $false `
                -Comment "Connettore per instradare email verso $SmartHost"
            
            Write-Host "Connettore outbound creato con successo!" -ForegroundColor Green
            return $connector
        }
        catch {
            Write-Error "Errore durante la creazione del connettore outbound: $_"
            exit 1
        }
    }
}

# Funzione per creare la regola di trasporto
function New-TransportRuleWithConnector {
    param(
        [string]$RuleName,
        [string]$DominioDestinazione,
        [string]$ConnectorName,
        [int]$Priority
    )
    
    Write-Host "`nVerifica esistenza regola di trasporto '$RuleName'..." -ForegroundColor Cyan
    
    $existingRule = Get-TransportRule -Identity $RuleName -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "Regola di trasporto '$RuleName' già esistente." -ForegroundColor Yellow
        
        $response = Read-Host "Vuoi rimuoverla e ricrearla? (S/N)"
        if ($response -eq 'S' -or $response -eq 's') {
            Remove-TransportRule -Identity $RuleName -Confirm:$false
            Write-Host "Regola esistente rimossa." -ForegroundColor Yellow
        }
        else {
            Write-Host "Operazione annullata." -ForegroundColor Yellow
            return $existingRule
        }
    }
    
    Write-Host "Creazione della regola di trasporto '$RuleName'..." -ForegroundColor Cyan
    
    try {
        $rule = New-TransportRule `
            -Name $RuleName `
            -Priority $Priority `
            -RecipientDomainIs $DominioDestinazione `
            -RouteMessageOutboundConnector $ConnectorName `
            -Enabled $true `
            -Comments "Instrada tutte le email dirette a $DominioDestinazione attraverso il connettore $ConnectorName"
        
        Write-Host "Regola di trasporto creata con successo!" -ForegroundColor Green
        return $rule
    }
    catch {
        Write-Error "Errore durante la creazione della regola di trasporto: $_"
        exit 1
    }
}

# Funzione per visualizzare il riepilogo della configurazione
function Show-ConfigurationSummary {
    param(
        [object]$Connector,
        [object]$Rule
    )
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "RIEPILOGO CONFIGURAZIONE" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`nCONNETTORE OUTBOUND:" -ForegroundColor Yellow
    Write-Host "  Nome: $($Connector.Name)"
    Write-Host "  SmartHosts: $($Connector.SmartHosts -join ', ')"
    Write-Host "  Abilitato: $($Connector.Enabled)"
    Write-Host "  TLS Settings: $($Connector.TlsSettings)"
    
    Write-Host "`nREGOLA DI TRASPORTO:" -ForegroundColor Yellow
    Write-Host "  Nome: $($Rule.Name)"
    Write-Host "  Priorità: $($Rule.Priority)"
    Write-Host "  Dominio destinazione: $($Rule.RecipientDomainIs -join ', ')"
    Write-Host "  Connettore usato: $($Rule.RouteMessageOutboundConnector)"
    Write-Host "  Stato: $($Rule.State)"
    
    Write-Host "`n========================================" -ForegroundColor Cyan
}

# MAIN SCRIPT
try {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "CONFIGURAZIONE REGOLA DI TRASPORTO" -ForegroundColor Cyan
    Write-Host "CON CONNETTORE OUTBOUND" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 1. Verifica e installa modulo
    Ensure-ExchangeOnlineModule
    
    # 2. Connessione a Exchange Online
    Connect-ToExchangeOnline
    
    # 3. Crea o verifica il connettore outbound
    $connector = New-OutboundConnectorIfNotExists -ConnectorName $OutboundConnectorName -SmartHost $SmartHost
    
    # 4. Crea la regola di trasporto
    $rule = New-TransportRuleWithConnector `
        -RuleName $TransportRuleName `
        -DominioDestinazione $DominioDestinazione `
        -ConnectorName $OutboundConnectorName `
        -Priority $Priority
    
    # 5. Mostra il riepilogo
    Show-ConfigurationSummary -Connector $connector -Rule $rule
    
    Write-Host "`nConfigurazione completata con successo!" -ForegroundColor Green
    Write-Host "Tutte le email dirette a @$DominioDestinazione saranno instradate attraverso il connettore '$OutboundConnectorName'." -ForegroundColor Green
}
catch {
    Write-Error "Errore durante l'esecuzione dello script: $_"
    exit 1
}
finally {
    # Opzionale: disconnessione da Exchange Online
    $disconnect = Read-Host "`nVuoi disconnetterti da Exchange Online? (S/N)"
    if ($disconnect -eq 'S' -or $disconnect -eq 's') {
        Disconnect-ExchangeOnline -Confirm:$false
        Write-Host "Disconnesso da Exchange Online." -ForegroundColor Gray
    }
}
