# Confronto tra Exchange Online, Exchange On‑Premises e Servizi Posta Microsoft 365

---

## Differenze principali

### ☁️ **Exchange Online (Cloud – parte di Microsoft 365)**

* **Hosting**: nei data center Microsoft (cloud pubblico).
* **Aggiornamenti**: completamente gestiti da Microsoft. Nessun patching, nessun aggiornamento da installare.
* **Scalabilità**: immediata. Aumenti e riduzioni di capacità senza interventi infrastrutturali.
* **High Availability / DR**: nativi e gestiti da Microsoft (multi-region, multi-datacenter).
* **Sicurezza**: funzionalità avanzate integrate (MFA, antispam/antimalware, Defender for 365).
* **Costi**: modello a **subscription per utente** → nessun server, nessun hardware.
* **Accessibilità**: accesso da ovunque, nativamente integrato con l’ecosistema Microsoft 365.
* **Limiti mailbox**: fino a 100 GB (E3/E5), archiviazione illimitata con auto-expanding archiving.

👉 Ideale se vuoi **zero manutenzione**, elevata sicurezza e scalabilità immediata.

---

### 🏢 **Exchange Server On-Premises**

* **Hosting**: nella tua infrastruttura, su server fisici o virtualizzati.
* **Aggiornamenti e patching**: a carico dell’organizzazione.
* **Scalabilità**: richiede investimenti in hardware, storage, licenze e configurazioni HA (DAG).
* **High Availability / DR**: completamente responsabilità del team IT.
* **Sicurezza**: devi implementare tu firewall, antispam, antimalware, MFA mediante soluzioni esterne.
* **Costi**:

  * Licenze Exchange Server (standard/enterprise).
  * **CAL** per utente.
  * Server, storage, backup, UPS, networking.
  * Manutenzione e personale IT.
* **Accessibilità**: richiede configurazioni specifiche per accesso remoto (reverse proxy, firewall, certificati).
* **Limiti mailbox**: variabili, dipendono dalla tua infrastruttura e storage.

👉 Ideale se hai **requisiti di compliance**, isolamento dei dati o integrazioni legacy che impongono infrastruttura locale.

----

### Tabella Comparativa

| Aspetto | Exchange Online | Exchange On‑Premises | Servizi posta Microsoft 365 |
|---|---|---|---|
| Hosting | Cloud Microsoft | Server di tua proprietà | Cloud Microsoft (suite) |
| Proprietà e gestione | Microsoft gestisce piattaforma e patch | Tu gestisci hardware, OS, Exchange | Microsoft gestisce; incluse app e servizi della suite |
| Aggiornamenti | Continui, automatici | Pianificati e manuali | Continui, automatici |
| Scalabilità | Elastica, per utente | Limitata da hardware | Elastica, per utente |
| SLA/Disponibilità | SLA Microsoft | Dipende dalla tua infrastruttura | SLA Microsoft, come Exchange Online |
| Storage cassetta postale | 50 GB (Piano 1), 100 GB (Piano 2); archiviazione online aggiuntiva | Dipende dalle risorse locali | Come Exchange Online, varia per piano della suite |
| Sicurezza e conformità | Protezioni cloud, anti‑malware, DLP (avanzate su piani superiori) | Controllo locale totale, ma richiede competenze | Protezioni cloud integrate + funzionalità aggiuntive della suite |
| Personalizzazione | Limitata a quanto consentito nel cloud | Massima (integrazioni, transport rules avanzate, estensioni) | Come Exchange Online |
| Modello di costo | Abbonamento per utente | Licenze + hardware + manutenzione | Abbonamento per utente, include altre app (Teams, SharePoint, Office) |
| Casi d’uso tipici | Rapidità, riduzione gestione, lavoro ibrido | Requisiti severi di controllo/dati on‑site | Email + produttività integrata nella suite |

---

## Che cos’è Exchange Online

Exchange Online è la versione cloud di Exchange erogata da Microsoft, acquistabile come piano standalone (Piano 1 o Piano 2) o inclusa nei piani Microsoft 365. Il Piano 1 offre cassette postali da 50 GB e Outlook sul web; il Piano 2 espande a 100 GB, con archiviazione su posto più ampia e funzionalità avanzate come la prevenzione della perdita di dati.

---

## Che cos’è Exchange On‑Premises

Exchange On‑Premises è installato su server che possiedi e gestisci tu, con pieno controllo sull’infrastruttura, la configurazione, le politiche di trasporto e l’integrazione con sistemi interni. Richiede pianificazione di capacità, patching, aggiornamenti e alta disponibilità gestiti dal tuo team IT, ma offre personalizzazioni e controllo dei dati che possono essere essenziali in alcuni scenari regolamentati.

---

## Che cosa si intende per “Servizi Posta Microsoft 365”

I “Servizi Posta Microsoft 365” indicano l’offerta email integrata nella suite Microsoft 365 (ex Office 365), che include Exchange Online più applicazioni e servizi come Teams, SharePoint, OneDrive e le app Office. Scegliendo la suite, l’email beneficia delle stesse caratteristiche di Exchange Online, con in più collaborazione e sicurezza interconnesse della piattaforma Microsoft 365.

---

## Vantaggi chiave a confronto

- **Operatività e manutenzione:** Exchange Online e Microsoft 365 riducono il carico operativo (patch, aggiornamenti, disponibilità gestite da Microsoft); On‑Prem richiede gestione completa ma consente scelte architetturali su misura.
- **Scalabilità e tempi di attivazione:** I servizi cloud scalano per utente e si attivano rapidamente; On‑Premises dipende da hardware, storage e rete locali.
- **Funzioni e limiti di cassetta postale:** Nei piani Exchange Online trovi quote predefinite (es. 50 GB o 100 GB) e archiviazione online, con funzionalità come Outlook sul web e opzioni di conformità; On‑Premises le definisci tu in base alle risorse e alla versione di Exchange.
- **Sicurezza e conformità:** Nel cloud hai protezioni integrate e, su piani superiori, DLP e funzioni avanzate; On‑Prem ti permette controlli personalizzati, ma richiede competenze e strumenti propri per eDiscovery, audit, anti‑malware e backup.
- **Costi e TCO:** Cloud = abbonamento prevedibile per utente; On‑Prem = CAPEX (hardware/licenze) + OPEX (energia, manutenzione, personale). La convenienza dipende da scala, requisiti e durata.
- **Integrazione e produttività:** La suite Microsoft 365 aggiunge collaborazione (Teams), contenuti (SharePoint/OneDrive) e app Office, creando un ecosistema unico oltre all’email.

---

## **👉 Quando scegliere cosa**

- **Scegliere Exchange On‑Premises** se hai requisiti stringenti di sovranità del dato, integrazioni locali particolari, o policy che impongono controllo completo sull’infrastruttura.
- **Scegliere Exchange Online** se vuoi ridurre gestione, avere alta disponibilità e costi prevedibili per utente, con funzionalità moderne e aggiornate nel cloud.
- **Scegliere servizi posta Microsoft 365** se l’email è parte di un’iniziativa più ampia di produttività e collaborazione, e vuoi un’unica suite con sicurezza e governance integrate.


### 🏢 **Exchange Server on-Premises**

👉 Hai vincoli di compliance estrema.
👉 Devi mantenere integrazioni legacy interne.
👉 Vuoi controllo completo su ogni dettaglio dell’infrastruttura.


### ☁️ **Exchange Online**

👉 Hai mail e calendari in cloud senza complicazioni.
👉 Ti va bene usare solo le funzionalità base di Exchange.

### ☁️ **Servizi di Posta Microsoft 365 (l’esperienza completa)**

👉 Vuoi non solo la posta, ma anche:

* sicurezza avanzata (Safe Links, Safe Attachments, DLP)
* collaboration Microsoft 365
* meeting Teams integrati con il calendario
* archiviazione illimitata e retention
* strumenti di compliance e legal hold
* Copilot per email, sintesi e automazioni

👉 Perfetto per aziende moderne, distribuite e con forte richiesta di sicurezza & produttività.

---

## Considerazioni Generali:

✔️ **Scegli Exchange Online se:**

* vuoi ridurre la complessità IT.
* cerchi alta disponibilità senza investire in infrastrutture.
* ti serve integrazione con Teams, SharePoint, OneDrive.
* vuoi sicurezza avanzata sempre aggiornata.

✔️ **Scegli Exchange Server On-Premises se:**

* hai vincoli di compliance estrema (es. dati che non possono lasciare il datacenter).
* devi integrare sistemi legacy non compatibili col cloud.
* vuoi completo controllo su storage, messaggistica e configurazioni a basso livello.