# Firma dei pacchetti DigiDesk

Le chiavi di firma si inseriscono **una volta sola** come Secrets del repository:
**Settings → Secrets and variables → Actions → New repository secret**.
I Secrets sono cifrati e GitHub li nasconde nei log. Non scriverli mai nel modulo
"Run workflow" né in un file del repository: il repository è pubblico.

A ogni compilazione si decide se firmare con la casella **Firma Windows** in
*Actions → DigiDesk Build → Run workflow*. Se la casella è spuntata ma i Secrets
mancano, la compilazione procede senza firmare.

---

## Windows — Azure Artifact Signing

Costo: piano Basic 9,99 $/mese. Gli exe firmati restano validi anche dopo aver
disdetto, perché la firma include la marca temporale.

### 1. Su Azure (portal.azure.com)

1. **Abbonamento**: serve un abbonamento Azure a pagamento (non gratuito/di prova).
2. **Registra il provider**: *Subscriptions* → il tuo abbonamento → *Resource providers*
   → `Microsoft.CodeSigning` → *Register*.
3. **Crea l'account di firma**: cerca *Artifact Signing Accounts* → *Create*.
   Regione consigliata: *West Europe* o *North Europe*. Piano: *Basic*.
4. **Verifica dell'identità**: nell'account → *Identity validations* → *Organization*
   → *New identity* → *Public*. Inserisci i dati legali di Digitech e un'email sul
   dominio aziendale. Richiede da 1 a 20 giorni lavorativi.
   Se il pulsante è disattivato, assegnati il ruolo *Artifact Signing Identity Verifier*.
5. **Profilo certificato**: nell'account → *Certificate profiles* → *Create* →
   *Public Trust*, scegliendo l'identità verificata al punto 4.
6. **Utente tecnico per GitHub**: *Microsoft Entra ID* → *App registrations* →
   *New registration* (nome ad es. `digidesk-github`). Poi
   *Certificates & secrets* → *New client secret* e copia subito il **Value**.
7. **Permesso di firma**: nell'account di firma → *Access control (IAM)* →
   *Add role assignment* → ruolo **Artifact Signing Certificate Profile Signer**
   → assegnalo all'app del punto 6.

### 2. Secrets da creare su GitHub

| Secret | Dove trovarlo |
|---|---|
| `AZURE_TENANT_ID` | App registration → *Directory (tenant) ID* |
| `AZURE_CLIENT_ID` | App registration → *Application (client) ID* |
| `AZURE_CLIENT_SECRET` | Il *Value* copiato al punto 6 |
| `AZURE_SIGNING_ENDPOINT` | Dipende dalla regione: West Europe `https://weu.codesigning.azure.net/`, North Europe `https://neu.codesigning.azure.net/` |
| `AZURE_SIGNING_ACCOUNT` | Nome dell'account creato al punto 3 |
| `AZURE_SIGNING_PROFILE` | Nome del profilo creato al punto 5 |

### Note

- Vengono firmati gli exe/dll interni e l'exe finale `digidesk-*-x86_64.exe`.
  La versione ARM64 non viene firmata (l'azione di Microsoft non supporta quei server).
- Il client secret scade (max 24 mesi): alla scadenza creane uno nuovo e aggiorna
  `AZURE_CLIENT_SECRET`.
- **Per smettere di pagare**: elimina l'account di firma (punto 3). La verifica
  dell'identità resta legata all'abbonamento, quindi in futuro basta ricreare
  account e profilo.

---

## Android

La build Android al momento non è tra le caselle di *DigiDesk Build*; il workflow
interno la supporta e la casella si può riaggiungere. Senza firma l'APK non si installa.

### 1. Crea la chiave (una volta sola)

Serve `keytool`, incluso in Java / Android Studio:

```bash
keytool -genkeypair -v -keystore digidesk.jks -alias digidesk -keyalg RSA -keysize 4096 -validity 10000
```

Converti il file in testo base64 (PowerShell), il risultato finisce negli appunti:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("digidesk.jks")) | Set-Clipboard
```

### 2. Secrets da creare su GitHub

| Secret | Valore |
|---|---|
| `ANDROID_SIGNING_KEY` | Il testo base64 del file `digidesk.jks` |
| `ANDROID_ALIAS` | `digidesk` (l'alias usato in `keytool`) |
| `ANDROID_KEY_STORE_PASSWORD` | La password scelta in `keytool` |
| `ANDROID_KEY_PASSWORD` | La stessa password |

### Importante

Conserva `digidesk.jks` e la password in un posto sicuro (non nel repository).
Se li perdi non potrai più aggiornare l'app sui dispositivi dove è installata:
andrebbe disinstallata e reinstallata.
