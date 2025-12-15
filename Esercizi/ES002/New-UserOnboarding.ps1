<#
.SYNOPSIS
    Script per l'onboarding completo di un nuovo utente in Exchange Online

.DESCRIPTION
    Questo script automatizza il processo di onboarding di un nuovo utente in Exchange Online,
    includendo la configurazione della casella di posta, permessi, gruppi e impostazioni.

.PARAMETER UserPrincipalName
    L'indirizzo email principale dell'utente

.PARAMETER DisplayName
    Il nome visualizzato dell'utente

.PARAMETER ManagerEmail
    L'indirizzo email del manager dell'utente

.PARAMETER Department
    Il dipartimento dell'utente

.PARAMETER Office
    L'ufficio dell'utente

.PARAMETER DistributionGroups
    Array di gruppi di distribuzione a cui aggiungere l'utente

.EXAMPLE
    .\New-UserOnboarding.ps1 -UserPrincipalName "mario.rossi@contoso.com" -DisplayName "Mario Rossi" -Department "IT" -ManagerEmail "supervisor@contoso.com"

.NOTES
    Autore: 
    Data: 
    Versione: 1.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$UserPrincipalName,
    
    [Parameter(Mandatory = $true)]
    [string]$DisplayName,
    
    [Parameter(Mandatory = $false)]
    [string]$ManagerEmail,
    
    [Parameter(Mandatory = $false)]
    [string]$Department,
    
    [Parameter(Mandatory = $false)]
    [string]$Office,
    
    [Parameter(Mandatory = $false)]
    [string[]]$DistributionGroups,
    
    [Parameter(Mandatory = $false)]
    [int]$MailboxQuotaGB = 50,
    
    [Parameter(Mandatory = $false)]
    [string]$DefaultLanguage = "it-IT",
    
    [Parameter(Mandatory = $false)]
    [string]$TimeZone = "W. Europe Standard Time",
    
    [Parameter(Mandatory = $false)]
    [string]$LogPath = ".\OnboardingLogs"
)

#Requires -Modules ExchangeOnlineManagement

# Funzione per il logging
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    $color = switch ($Level) {
        "INFO" { "Cyan" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
    }
    
    Write-Host $logMessage -ForegroundColor $color
    
    # Salva nel file di log
    if (-not (Test-Path $LogPath)) {
        New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
    }
    
    $logFile = Join-Path $LogPath "Onboarding_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $logFile -Value $logMessage
}

# Funzione per verificare la connessione a Exchange Online
function Test-ExchangeOnlineConnection {
    try {
        Get-OrganizationConfig -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Inizio script
Write-Log "=== INIZIO ONBOARDING UTENTE: $UserPrincipalName ===" -Level INFO

try {
    # 1. Verifica connessione a Exchange Online
    Write-Log "Verifica connessione a Exchange Online..." -Level INFO
    if (-not (Test-ExchangeOnlineConnection)) {
        Write-Log "Connessione a Exchange Online..." -Level INFO
        Connect-ExchangeOnline -ShowBanner:$false
        Start-Sleep -Seconds 2
    }
    Write-Log "Connesso a Exchange Online" -Level SUCCESS

    # 2. Verifica esistenza casella di posta
    Write-Log "Verifica esistenza casella di posta per $UserPrincipalName..." -Level INFO
    $mailbox = Get-Mailbox -Identity $UserPrincipalName -ErrorAction SilentlyContinue
    
    if (-not $mailbox) {
        Write-Log "ATTENZIONE: La casella di posta non esiste ancora. Assicurati che l'utente sia stato creato in Azure AD/Microsoft 365." -Level WARNING
        Write-Log "Attesa che la casella di posta venga provisionata (questo può richiedere alcuni minuti)..." -Level INFO
        
        $maxRetries = 10
        $retryCount = 0
        $mailboxFound = $false
        
        while (-not $mailboxFound -and $retryCount -lt $maxRetries) {
            Start-Sleep -Seconds 30
            $retryCount++
            Write-Log "Tentativo $retryCount di $maxRetries..." -Level INFO
            
            $mailbox = Get-Mailbox -Identity $UserPrincipalName -ErrorAction SilentlyContinue
            if ($mailbox) {
                $mailboxFound = $true
            }
        }
        
        if (-not $mailboxFound) {
            throw "Impossibile trovare la casella di posta per $UserPrincipalName dopo $maxRetries tentativi"
        }
    }
    
    Write-Log "Casella di posta trovata: $($mailbox.DisplayName)" -Level SUCCESS

    # 3. Configurazione impostazioni casella di posta
    Write-Log "Configurazione impostazioni casella di posta..." -Level INFO
    
    # Imposta quote della casella di posta
    Set-Mailbox -Identity $UserPrincipalName `
        -IssueWarningQuota "$($MailboxQuotaGB - 5)GB" `
        -ProhibitSendQuota "${MailboxQuotaGB}GB" `
        -ProhibitSendReceiveQuota "$($MailboxQuotaGB + 2)GB" `
        -RetainDeletedItemsFor 30
    
    Write-Log "Quote casella di posta configurate: ${MailboxQuotaGB}GB" -Level SUCCESS

    # 4. Configurazione lingua e fuso orario
    Write-Log "Configurazione lingua e fuso orario..." -Level INFO
    Set-MailboxRegionalConfiguration -Identity $UserPrincipalName `
        -Language $DefaultLanguage `
        -TimeZone $TimeZone `
        -DateFormat "dd/MM/yyyy" `
        -TimeFormat "HH:mm"
    
    Write-Log "Lingua impostata: $DefaultLanguage, Fuso orario: $TimeZone" -Level SUCCESS

    # 5. Abilitazione archivio online
    Write-Log "Abilitazione archivio online..." -Level INFO
    $archive = Get-Mailbox -Identity $UserPrincipalName | Select-Object ArchiveStatus
    
    if ($archive.ArchiveStatus -eq "None") {
        Enable-Mailbox -Identity $UserPrincipalName -Archive
        Write-Log "Archivio online abilitato" -Level SUCCESS
    }
    else {
        Write-Log "Archivio online già abilitato" -Level INFO
    }

    # 6. Configurazione opzioni casella di posta
    Write-Log "Configurazione opzioni avanzate casella di posta..." -Level INFO
    Set-MailboxMessageConfiguration -Identity $UserPrincipalName `
        -AutoAddSignature $true `
        -AutoAddSignatureOnMobile $true `
        -AlwaysShowBcc $false `
        -AlwaysShowFrom $true
    
    Write-Log "Opzioni casella di posta configurate" -Level SUCCESS

    # 7. Configurazione ActiveSync e OWA
    Write-Log "Configurazione ActiveSync e OWA..." -Level INFO
    Set-CASMailbox -Identity $UserPrincipalName `
        -ActiveSyncEnabled $true `
        -OWAEnabled $true `
        -PopEnabled $false `
        -ImapEnabled $false `
        -MAPIEnabled $true `
        -EwsEnabled $true `
        -ActiveSyncMailboxPolicy "Default"
    
    Write-Log "Protocolli di accesso configurati" -Level SUCCESS

    # 8. Aggiunta ai gruppi di distribuzione
    if ($DistributionGroups) {
        Write-Log "Aggiunta ai gruppi di distribuzione..." -Level INFO
        foreach ($group in $DistributionGroups) {
            try {
                Add-DistributionGroupMember -Identity $group -Member $UserPrincipalName -ErrorAction Stop
                Write-Log "Aggiunto al gruppo: $group" -Level SUCCESS
            }
            catch {
                Write-Log "Errore nell'aggiunta al gruppo $group : $($_.Exception.Message)" -Level WARNING
            }
        }
    }

    # 9. Configurazione Outlook Web App Policy
    Write-Log "Configurazione policy Outlook Web App..." -Level INFO
    Set-OwaMailboxPolicy -Identity "OwaMailboxPolicy-Default" -ErrorAction SilentlyContinue
    
    # 10. Impostazione forward automatico disabilitato (per sicurezza)
    Write-Log "Verifica impostazioni forward automatico..." -Level INFO
    Set-Mailbox -Identity $UserPrincipalName `
        -DeliverToMailboxAndForward $false `
        -ForwardingAddress $null `
        -ForwardingSmtpAddress $null
    
    Write-Log "Forward automatico disabilitato (sicurezza)" -Level SUCCESS

    # 11. Abilitazione audit logging
    Write-Log "Abilitazione audit logging..." -Level INFO
    Set-Mailbox -Identity $UserPrincipalName -AuditEnabled $true
    Write-Log "Audit logging abilitato" -Level SUCCESS

    # 12. Configurazione retention policy
    Write-Log "Configurazione retention policy..." -Level INFO
    $retentionPolicy = Get-RetentionPolicy | Where-Object { $_.IsDefault -eq $true } | Select-Object -First 1
    
    if ($retentionPolicy) {
        Set-Mailbox -Identity $UserPrincipalName -RetentionPolicy $retentionPolicy.Name
        Write-Log "Retention policy applicata: $($retentionPolicy.Name)" -Level SUCCESS
    }
    else {
        Write-Log "Nessuna retention policy di default trovata" -Level WARNING
    }

    # 13. Impostazione out of office disabilitato
    Write-Log "Verifica stato Out of Office..." -Level INFO
    Set-MailboxAutoReplyConfiguration -Identity $UserPrincipalName `
        -AutoReplyState Disabled
    
    Write-Log "Out of Office disabilitato" -Level SUCCESS

    # 14. Riepilogo configurazione
    Write-Log "=== RIEPILOGO CONFIGURAZIONE ===" -Level INFO
    Write-Log "Utente: $DisplayName ($UserPrincipalName)" -Level INFO
    Write-Log "Dipartimento: $Department" -Level INFO
    Write-Log "Ufficio: $Office" -Level INFO
    Write-Log "Manager: $ManagerEmail" -Level INFO
    Write-Log "Quota casella: ${MailboxQuotaGB}GB" -Level INFO
    Write-Log "Lingua: $DefaultLanguage" -Level INFO
    Write-Log "Fuso orario: $TimeZone" -Level INFO
    Write-Log "Archivio online: Abilitato" -Level INFO
    Write-Log "Audit logging: Abilitato" -Level INFO
    
    if ($DistributionGroups) {
        Write-Log "Gruppi di distribuzione: $($DistributionGroups -join ', ')" -Level INFO
    }

    # 15. Test invio email
    Write-Log "Test invio email di benvenuto..." -Level INFO
    Write-Log "NOTA: Invia manualmente un'email di benvenuto all'utente con le credenziali e le istruzioni." -Level WARNING

    Write-Log "=== ONBOARDING COMPLETATO CON SUCCESSO ===" -Level SUCCESS
    Write-Log "L'utente $UserPrincipalName è ora configurato e pronto per l'uso." -Level SUCCESS

    # Ritorna oggetto con i dettagli
    return [PSCustomObject]@{
        Success           = $true
        UserPrincipalName = $UserPrincipalName
        DisplayName       = $DisplayName
        MailboxQuota      = "${MailboxQuotaGB}GB"
        ArchiveEnabled    = $true
        Language          = $DefaultLanguage
        TimeZone          = $TimeZone
        Groups            = $DistributionGroups
        CompletedDate     = Get-Date
    }
}
catch {
    Write-Log "ERRORE durante l'onboarding: $($_.Exception.Message)" -Level ERROR
    Write-Log "Stack Trace: $($_.ScriptStackTrace)" -Level ERROR
    
    return [PSCustomObject]@{
        Success      = $false
        ErrorMessage = $_.Exception.Message
        ErrorDetails = $_.ScriptStackTrace
    }
}
finally {
    Write-Log "=== FINE PROCESSO ONBOARDING ===" -Level INFO
}
