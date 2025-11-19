
# Managing the Transport Pipeline

Nel contesto Microsoft, la **transport pipeline** rappresenta l’intero percorso che un messaggio e-mail compie all’interno di **Exchange Online**, **Exchange Server on-premises** o in un ambiente **ibrido**.

È il meccanismo che gestisce:

* routing delle email
* sicurezza e compliance
* conversione dei formati
* applicazione di regole e policy
* anti-spam / anti-malware
* recapito finale alle mailbox

---

## **1. Che cos’è la Transport Pipeline in Exchange / Microsoft 365**

Nei sistemi Exchange, la transport pipeline è formata da una serie di **servizi, ruoli e agenti** responsabili di ricevere, processare, filtrare e consegnare la posta.

In parole semplici:

*"È il sistema che prende un’email in ingresso e la porta destinazione applicando tutte le policy aziendali e di sicurezza necessarie."*

---

## **2. Componenti principali della Transport Pipeline**
---

### 🔹 **2.1 Transport Services (Exchange Server)**

In Exchange Server (on-premises) i servizi chiave sono:

#### **➤ Front End Transport Service (CAS)**

* Accetta connessioni SMTP in ingresso
* Non elabora messaggi, solo proxy
* Usato per il traffico esterno

#### **➤ Transport Service (Mailbox Server)**

Il “motore” della posta. Gestisce:

* routing messaggi
* regole di trasporto
* antimalware integrato
* conversioni di formato (MIME ↔ MAPI)
* consegna alla mailbox database

#### **➤ Mailbox Transport Submission e Delivery**

* **Submission**: prende messaggi da Outbox (MAPI) e li invia al Transport Service
* **Delivery**: recapita i messaggi al database mailbox

---

### 🔹 **2.2 Transport Pipeline in Exchange Online (Microsoft 365)**

In cloud troviamo componenti analoghi, ma potenziati da infrastruttura Microsoft e filtrazione avanzata:

#### **➤ Front-End Servers (SMTP Ingress)**

* Accettano email dall’esterno
* Autenticazione/TLS
* Rate limiting e protezione da attacchi

#### **➤ Exchange Online Transport**

* Routing intelligente su datacenter globali
* Regole di flusso (Transport Rules)
* Anti-spam/anti-malware
* Filtering via **Microsoft Defender for Office 365**
* Data Loss Prevention
* Safe Attachments / Safe Links

#### **➤ Mailbox Delivery Fabric**

* Consegna al database dentro Azure
* Indici, ricerca e archiviazione

---

## **3. Transport Channels e Routing**

### 🔹 **Exchange Online**

* Routing globale tramite **datacenter multipli**
* Load balancing automatico
* TLS obbligatorio ove possibile (opportunistic o enforced)
* Hybrid mail flow (se on-prem è presente)

### 🔹 **Exchange Server On-prem**

* Connettori organizzativi
* Send Connector / Receive Connector
* Routing basato su AD
* Edge Transport opzionale per DMZ

---

## **4. Transport Rules e Policies**

Le **Regole di Trasporto** (Exchange Transport Rules) consentono di applicare policy al passaggio dei messaggi, come:

* bloccare o reindirizzare messaggi
* applicare disclaimers
* classificare contenuti
* applicare DLP (solo Online / M365)
* inviare alert agli amministratori

Nei sistemi Microsoft 365 l’engine è molto più completo grazie alla suite **Microsoft Purview**.

---

## **5. Tipologie di Transport Services (Applicate a Microsoft)**

| Tipo di Trasporto          | Exchange Server                 | Exchange Online                       |
| -------------------------- | ------------------------------- | ------------------------------------- |
| **Best Effort**            | Intra-org routing base          | SMTP routing globale Microsoft        |
| **Guaranteed Delivery**    | Shadow Redundancy, Safety Net   | Continuous Replication su scala cloud |
| **Transactional Delivery** | Submit/Delivery + database ACID | Fabric a resilienza multipla in Azure |
| **Secure Transport**       | TLS + opportunistic encryption  | TLS 1.2+, MTA-STS, DANE, DKIM, DMARC  |

---

## **6. Perché la Transport Pipeline è cruciale in Microsoft 365 / Exchange**

* Garantisce **alta affidabilità** e zero perdita di email
* Assicura **resilienza globale** in cloud
* Permette **compliance avanzata** (GDPR, DLP, auditing)
* Protegge da malware, phishing, spoofing
* Permette scenari **ibridi** senza complessità aggiuntive
* Ottimizza routing, prestazioni e consegna

---

# **7. Esempi pratici**

### **✔ Esempio 1: Mail Flow ibrido**

1. Email arriva su Exchange Online
2. Viene filtrata da Defender
3. Regole di transport applicate
4. Instradata verso Exchange Server tramite Hybrid Agent
5. Consegna alla mailbox on-prem

---

### **✔ Esempio 2: Mail Flow interamente cloud**

1. SMTP ingress → datacenter Microsoft
2. Anti-spam/AML
3. Posta passa nella pipeline (regole, DLP, encryption, journaling)
4. Consegna nella mailbox Exchange Online

---

### **✔ Esempio 3: Exchange Server on-prem**

1. Receive Connector accetta il messaggio
2. Transport Service lo elabora e invia
3. Safety Net/Shadow Redundancy garantiscono resilienza
4. Mailbox Transport Delivery lo salva nel DB


