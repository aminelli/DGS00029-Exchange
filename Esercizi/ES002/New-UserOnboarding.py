"""
New-UserOnboarding.py

Script Python che esegue l'onboarding di un nuovo utente in Exchange Online
usando PowerShell (ExchangeOnlineManagement) in background.

Prerequisiti:
- PowerShell Core (`pwsh`) o Windows PowerShell disponibile nel PATH
- Modulo PowerShell `ExchangeOnlineManagement` installato
- Permessi amministrativi in Exchange Online

Lo script costruisce uno script PowerShell e lo esegue in una singola sessione
per mantenere la connessione e applicare le stesse configurazioni del
lo script PowerShell originale.

Nota: il provisioning reale richiede credenziali e ambiente Azure AD/M365.
"""

from __future__ import annotations
import argparse
import logging
import shutil
import subprocess
import sys
import tempfile
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("onboarding")


def ps_escape(s: Optional[str]) -> str:
    if s is None:
        return ""
    # Escape single quotes for PowerShell single-quoted strings
    return s.replace("'", "''")


def find_pwsh_executable() -> Optional[str]:
    # Prefer `pwsh` (PowerShell Core), fallback to `powershell`
    for name in ("pwsh", "powershell"):
        path = shutil.which(name)
        if path:
            return path
    return None


def run_pwsh_script(script: str) -> subprocess.CompletedProcess:
    pwsh = find_pwsh_executable()
    if not pwsh:
        raise RuntimeError("Nessun eseguibile PowerShell trovato nel PATH. Installa PowerShell Core (pwsh) o assicurati che powershell sia nel PATH.")

    # Run the script using -NoProfile to avoid user profile side-effects
    proc = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    return proc


def build_ps_script(
    user_principal_name: str,
    display_name: str,
    manager_email: Optional[str],
    department: Optional[str],
    office: Optional[str],
    distribution_groups: Optional[List[str]],
    mailbox_quota_gb: int,
    default_language: str,
    time_zone: str,
) -> str:
    # escape values for embedding in single-quoted PowerShell strings
    upn = ps_escape(user_principal_name)
    dn = ps_escape(display_name)
    mgr = ps_escape(manager_email) if manager_email else ""
    dept = ps_escape(department) if department else ""
    off = ps_escape(office) if office else ""
    groups_array = ";".join([ps_escape(g) for g in distribution_groups]) if distribution_groups else ""

    ps = f"""
$ErrorActionPreference = 'Stop'
Write-Output 'CONNECTING'
Connect-ExchangeOnline -ShowBanner:$false
Write-Output 'CONNECTED'

try {{
    Write-Output 'CHECK_MAILBOX'
    $mailbox = Get-Mailbox -Identity '{upn}' -ErrorAction SilentlyContinue
    if (-not $mailbox) {{
        Write-Output 'MAILBOX_NOT_FOUND'
        $maxRetries = 10
        $retry = 0
        $found = $false
        while (-not $found -and $retry -lt $maxRetries) {{
            Start-Sleep -Seconds 30
            $retry++
            Write-Output "Retry $retry/$maxRetries"
            $mailbox = Get-Mailbox -Identity '{upn}' -ErrorAction SilentlyContinue
            if ($mailbox) {{ $found = $true }}
        }}
        if (-not $found) {{ throw "Impossibile trovare la casella di posta per {upn} dopo $maxRetries tentativi" }}
    }}
    else {{
        Write-Output "MAILBOX_FOUND:$($mailbox.DisplayName)"
    }}

    # Imposta quote
    Set-Mailbox -Identity '{upn}' -IssueWarningQuota "$({mailbox_quota_gb - 5})GB" -ProhibitSendQuota "{mailbox_quota_gb}GB" -ProhibitSendReceiveQuota "$({mailbox_quota_gb + 2})GB" -RetainDeletedItemsFor 30
    Write-Output 'SET_QUOTAS'

    # Lingua e fuso orario
    Set-MailboxRegionalConfiguration -Identity '{upn}' -Language '{ps_escape(default_language)}' -TimeZone '{ps_escape(time_zone)}' -DateFormat 'dd/MM/yyyy' -TimeFormat 'HH:mm'
    Write-Output 'SET_REGIONAL'

    # Abilita archivio se necessario
    $archive = Get-Mailbox -Identity '{upn}' | Select-Object -ExpandProperty ArchiveStatus
    if ($archive -eq 'None') {{ Enable-Mailbox -Identity '{upn}' -Archive; Write-Output 'ARCHIVE_ENABLED' }} else {{ Write-Output 'ARCHIVE_ALREADY' }}

    # Opzioni casella
    # Nota: Set-MailboxMessageConfiguration potrebbe non esporre tutte le stesse opzioni via API
    Write-Output 'CONFIGURE_MESSAGE_OPTIONS'

    # CAS/OWA
    Set-CASMailbox -Identity '{upn}' -ActiveSyncEnabled $true -OWAEnabled $true -PopEnabled $false -ImapEnabled $false -MAPIEnabled $true -EwsEnabled $true
    Write-Output 'SET_CAS'

    # Aggiunta a gruppi di distribuzione
    if ('{groups_array}' -ne '') {{
        $groups = '{groups_array}'.Split(';') | Where-Object {{ $_ -ne '' }}
        foreach ($g in $groups) {{
            try {{ Add-DistributionGroupMember -Identity $g -Member '{upn}' -ErrorAction Stop; Write-Output "ADDED_TO_GROUP:$g" }}
            catch {{ Write-Warning "Errore aggiunta a gruppo $g: $($_.Exception.Message)" }}
        }}
    }}

    # Disabilita forward automatico
    Set-Mailbox -Identity '{upn}' -DeliverToMailboxAndForward $false -ForwardingAddress $null -ForwardingSmtpAddress $null
    Write-Output 'DISABLED_FORWARDS'

    # Abilita audit
    Set-Mailbox -Identity '{upn}' -AuditEnabled $true
    Write-Output 'AUDIT_ENABLED'

    # Applica retention policy di default se presente
    $rp = Get-RetentionPolicy | Where-Object {{ $_.IsDefault -eq $true }} | Select-Object -First 1
    if ($rp) {{ Set-Mailbox -Identity '{upn}' -RetentionPolicy $rp.Name; Write-Output "RETENTION_APPLIED:$($rp.Name)" }} else {{ Write-Output 'NO_RETENTION_POLICY' }}

    # Disabilita out of office
    Set-MailboxAutoReplyConfiguration -Identity '{upn}' -AutoReplyState Disabled
    Write-Output 'AUTO_REPLY_DISABLED'

    Write-Output 'ONBOARDING_SUCCESS'
}}
catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
finally {{
    # Optional: Disconnect-ExchangeOnline -Confirm:$false
}}
"""
    return ps


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Onboarding Exchange Online via PowerShell (invocato da Python)")
    parser.add_argument("-u", "--user", required=True, help="UserPrincipalName (es: mario.rossi@contoso.com)")
    parser.add_argument("-n", "--display-name", required=True, help="Display name")
    parser.add_argument("-m", "--manager", help="Manager email")
    parser.add_argument("-d", "--department", help="Department")
    parser.add_argument("-o", "--office", help="Office")
    parser.add_argument("-g", "--groups", nargs="*", help="Distribution groups")
    parser.add_argument("--quota", type=int, default=50, help="Mailbox quota GB (default 50)")
    parser.add_argument("--lang", default="it-IT", help="Default language (default it-IT)")
    parser.add_argument("--tz", default="W. Europe Standard Time", help="Time zone (default W. Europe Standard Time)")

    args = parser.parse_args(argv)

    ps_script = build_ps_script(
        user_principal_name=args.user,
        display_name=args.display_name,
        manager_email=args.manager,
        department=args.department,
        office=args.office,
        distribution_groups=args.groups,
        mailbox_quota_gb=args.quota,
        default_language=args.lang,
        time_zone=args.tz,
    )

    logger.info("Eseguo PowerShell (Exchange Online). Verrà richiesta autenticazione se necessario.")

    # For safety, write the script to a temp file and execute it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as tf:
        tf.write(ps_script)
        tf.flush()
        ps_path = tf.name

    # Run using pwsh/powershell
    try:
        # Use the script file so quoting is simpler
        pwsh = find_pwsh_executable()
        if not pwsh:
            logger.error("PowerShell non trovato nel PATH. Installa pwsh o powershell.")
            return 2

        cmd = [pwsh, "-NoProfile", "-NonInteractive", "-File", ps_path]
        logger.debug("Eseguo: %s", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)

        logger.info(proc.stdout)
        if proc.returncode != 0:
            logger.error("PowerShell ha restituito codice %d", proc.returncode)
            logger.error(proc.stderr)
            return proc.returncode

        logger.info("Onboarding completato con successo.")
        return 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
