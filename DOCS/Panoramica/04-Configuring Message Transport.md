# 🔷 **Configuring Message Transport in Microsoft 365, Exchange Online e Exchange Server**

La configurazione del *message transport* definisce **come le email vengono ricevute, elaborate e inviate** all’interno dell’organizzazione.
È un punto critico sia per la **sicurezza**, sia per la **connettività** (interna, esterna, ibrida) e per eventuali sistemi terzi (antispam esterni, appliance firewall, SMTP relay).

In termini pratici, significa configurare:

* flusso di posta (mail flow)
* connettori (Send/Receive)
* routing interno ed esterno
* regole e policy di trasporto
* sicurezza TLS e autenticazioni
* relay e smarthost
* integrazione ibrida

---

# 🔶 **1. Configurare Message Transport in Exchange Online (Microsoft 365)**

In Exchange Online la configurazione si basa sul principio del **Mail Flow Moderno**:

---

## **1.1 Receive Connectors (virtualizzati)**

In Exchange Online non si configurano direttamente receive connector, ma:

* MX record del dominio
* Autenticazione SMTP
* Permessi per SMTP AUTH (se necessario)
* Restrizioni di invio da dispositivi (SMTP Submission, porta 587)

### Controlli importanti:

* TLS obbligatorio per la quasi totalità dei flussi
* Supporto per MTA-STS e DANE
* Filtri antispam/antimalware integrati

---

## **1.2 Send Connectors (gestiti dal sistema)**

Exchange Online usa il proprio routing intelligente.
L’amministratore può configurare solo casi specifici:

### **➤ Connettori verso sistemi esterni**

* Smarthost in uscita verso provider terzi
* Connettori certificati TLS (partner connectors)
* Connettori a scopo di compliance o journaling

---

## **1.3 Configurazione Message Transport – scenari principali**

### **➤ 1.3.1 Mail flow interno (cloud-to-cloud)**

Zero configurazione: tutto gestito dall’infrastruttura Microsoft.

### **➤ 1.3.2 Mail flow in ingresso (internet → M365)**

1. Cambiare l’MX verso `<tenant>.mail.protection.outlook.com`
2. Validare il dominio
3. Configurare SPF, DKIM, DMARC
4. Eventuali connettori da partner (TLS)

### **➤ 1.3.3 Mail flow in uscita (M365 → internet)**

Normalmente automatico.
Possibili customizzazioni:

* uscita attraverso smarthost esterno
* routing verso appliance on-prem
* TLS obbligatorio per domini specifici

### **➤ 1.3.4 Relay SMTP da dispositivi (scanner, IoT, applicazioni)**

Tre modalità ufficiali:

* SMTP AUTH (porta 587)
* Direct Send (porta 25, solo verso destinatari interni)
* SMTP Relay autenticato tramite indirizzo IP (connettore personalizzato)

---

# 🔶 **2. Configurare Message Transport in Exchange Server (on-premises)**

Exchange Server offre controllo completo su come la posta viene gestita, perché utilizza:

* **Receive Connectors**
* **Send Connectors**
* **Edge Transport** (opzionale)
* **Transport Services** sui server Mailbox

---

## **2.1 Receive Connectors**

Serve per stabilire chi può inviare posta **al server** e con quali permessi.

Tipici scenari:

| Tipo                                          | Uso                                        |
| --------------------------------------------- | ------------------------------------------ |
| **Default Frontend Receive Connector**        | ricezione posta da Internet                |
| **Client Frontend Connector**                 | invio da Outlook, SMTP Submission          |
| **Custom Connector per applicazioni interne** | relay da sistemi interni                   |
| **Authenticated Connector**                   | richiesto per applicazioni che usano login |

### Parametri fondamentali:

* IP binding
* Porta (25 o 587)
* Permessi (Anonymous, ExchangeUsers, Partner)
* Autenticazione (TLS, Basic, Integrated)
* Dimensioni messaggi, rate limit

---

## **2.2 Send Connectors**

Definiscono **dove** Exchange Server deve inviare la posta uscente.

Tipici scenari:

| Tipo                                | Scopo                                |
| ----------------------------------- | ------------------------------------ |
| **Internet Send Connector**         | inviare email a domini esterni       |
| **Smarthost Connector**             | instradare posta tramite terze parti |
| **Hub → Edge Connector**            | scenari con Edge Transport           |
| **Connector verso Exchange Online** | flusso ibrido                        |

### Parametri chiave:

* Tipo di routing (MX direct vs Smarthost)
* Metodo TLS (Opportunistic, Enforced, Certificate-based)
* Cost (priorità dei connettori)

---

## **2.3 Edge Transport Role (opzionale)**

Installato in DMZ, gestisce:

* filtering
* antispam
* regole di trasporto pre-consegna
* connettori EdgeSync verso AD

È molto utile in ambienti ad alta sicurezza.

---

# 🔶 **3. Configurare Message Transport in ambienti ibridi (Exchange Online + Exchange Server)**

È lo scenario più delicato e tecnico.

Microsoft raccomanda:

### **3.1 Hybrid Configuration Wizard (HCW)**

Il tool genera automaticamente:

* Send Connector *Exchange Online to On-Premises*
* Receive Connector *On-Premises to Exchange Online*
* Federazione certificati
* Autenticazione OAuth
* Regole per evitare loop e doppia scansione

### **3.2 Flusso consigliato**

🔹 *Inbound Internet Mail → M365 → On-prem (solo se mailbox locale)*
🔹 *Outbound On-prem → M365 → Internet*

### Motivi:

* antivirus/antispam moderni
* protezione ATP
* regole di compliance nel cloud
* maggiore resilienza

---

# 🔶 **4. Sicurezza nel Message Transport**

Indipendentemente dall’ambiente, le configurazioni moderne richiedono:

### **Obbligatorio**

* TLS 1.2 o superiore
* Certificati validi pubblici
* SPF + DKIM + DMARC
* Restrizioni su relay non autenticati
* Rate limiting per connettori aperti

### **Raccomandato**

* MTA-STS (Exchange Online)
* DANE
* Zero Trust Mail Flow
* Journaling + auditing (Purview)
* Blocco SMTP AUTH se non necessario

---

# 🔶 **5. Regole di Trasporto (Exchange Transport Rules)**

La configurazione del message transport include anche l’applicazione di *policy*:

* DLP (Data Loss Prevention)
* Encryption (OME / sensibilità)
* Avvisi automatici
* Redirezione e firma messaggi
* Archiviazione e journaling

In Microsoft 365 le regole sono integrate con **Microsoft Purview** per la compliance avanzata.

---

# 🔷 **Riepilogo**

“Configuring Message Transport” significa:

* definire come Exchange invia e riceve email
* configurare connettori, routing, sicurezza
* applicare policy di flusso, sicurezza e compliance
* gestire scenari cloud, on-prem e ibridi
* prevenire relay aperti, failure, perdite di posta

In Exchange Online molta configurazione è automatizzata.
In Exchange Server il controllo è totale.
In ambienti ibridi serve precisione nella configurazione dei connettori e della sicurezza TLS.

---
