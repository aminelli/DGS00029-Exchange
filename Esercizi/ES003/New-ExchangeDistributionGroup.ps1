# Script PowerShell per creare un gruppo di distribuzione su Exchange Online
# Requisiti: Modulo ExchangeOnlineManagement installato
# Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber

<#
.SYNOPSIS
    Crea un nuovo gruppo di distribuzione su Exchange Online
.DESCRIPTION
    Questo script si connette a Exchange Online e crea un gruppo di distribuzione con membri
.EXAMPLE
    .\New-ExchangeDistributionGroup.ps1
#>

# Parametri configurabili
$GroupName = "Marketing Team"
$GroupAlias = "marketing-team"
$GroupEmail = "marketing@contoso.com"
$GroupDisplayName = "Marketing Team - Italy"
$GroupDescription = "Gruppo di distribuzione per il team Marketing"

# Array di membri da aggiungere (indirizzi email)
$Members = @(
    "user1@contoso.com",
    "user2@contoso.com",
    "user3@contoso.com"
)

try {
    Write-Host "Connessione a Exchange Online..." -ForegroundColor Cyan
    
    # Connessione a Exchange Online
    Connect-ExchangeOnline -ShowBanner:$false
    
    Write-Host "Creazione del gruppo di distribuzione..." -ForegroundColor Yellow
    
    # Creazione del gruppo di distribuzione
    $NewGroup = New-DistributionGroup -Name $GroupName `
                                      -Alias $GroupAlias `
                                      -PrimarySmtpAddress $GroupEmail `
                                      -DisplayName $GroupDisplayName `
                                      -Notes $GroupDescription `
                                      -Type "Distribution" `
                                      -MemberJoinRestriction "Closed" `
                                      -MemberDepartRestriction "Closed"
    
    Write-Host "Gruppo creato con successo: $($NewGroup.PrimarySmtpAddress)" -ForegroundColor Green
    
    # Aggiunta membri al gruppo
    Write-Host "`nAggiunta membri al gruppo..." -ForegroundColor Yellow
    foreach ($Member in $Members) {
        try {
            Add-DistributionGroupMember -Identity $GroupAlias -Member $Member
            Write-Host "  [+] Aggiunto: $Member" -ForegroundColor Green
        }
        catch {
            Write-Host "  [!] Errore nell'aggiungere $Member : $_" -ForegroundColor Red
        }
    }
    
    # Visualizzazione informazioni del gruppo
    Write-Host "`nInformazioni del gruppo:" -ForegroundColor Cyan
    Get-DistributionGroup -Identity $GroupAlias | Format-List Name, PrimarySmtpAddress, DisplayName, Notes
    
    # Visualizzazione membri del gruppo
    Write-Host "`nMembri del gruppo:" -ForegroundColor Cyan
    Get-DistributionGroupMember -Identity $GroupAlias | Format-Table Name, PrimarySmtpAddress -AutoSize
    
    Write-Host "`nOperazione completata con successo!" -ForegroundColor Green
}
catch {
    Write-Host "Errore durante l'esecuzione dello script: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    # Disconnessione da Exchange Online
    Write-Host "`nDisconnessione da Exchange Online..." -ForegroundColor Cyan
    Disconnect-ExchangeOnline -Confirm:$false
}
