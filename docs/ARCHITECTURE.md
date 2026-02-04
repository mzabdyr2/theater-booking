# 🎭 Theater Booking System - Dokumentacja Projektu

## 📋 Informacje podstawowe

| Pole               | Wartość                             |
| ------------------ | ----------------------------------- |
| **Nazwa projektu** | Theater Booking System              |
| **Temat**          | System rezerwacji biletów do teatru |
| **Chmura**         | Microsoft Azure                     |
| **Zespół**         | Student (projekt indywidualny)      |
| **Data**           | Luty 2026                           |

---

## 1. 🎯 Opis projektu

### Problem

Teatry potrzebują nowoczesnego systemu do rezerwacji biletów online, który pozwala widzom samodzielnie wybierać miejsca na sali i płacić za bilety bez konieczności wizyty w kasie.

### Rozwiązanie

System webowy umożliwiający:

- Przeglądanie repertuaru wydarzeń
- Interaktywny wybór miejsc na planie sali
- Rezerwację i płatność online
- Otrzymanie potwierdzenia z numerem rezerwacji

### Główne funkcjonalności:

1. **Katalog wydarzeń** - lista spektakli z opisami i datami
2. **Mapa miejsc** - interaktywna wizualizacja sali z kategoriami miejsc
3. **System rezerwacji** - tworzenie rezerwacji z walidacją dostępności
4. **Płatności Stripe** - bezpieczne płatności kartą
5. **Potwierdzenia** - generowanie unikalnych kodów rezerwacji

---

## 2. 🏗 Architektura systemu

### Diagram architektury

```
                                    ┌─────────────────────────────────────────┐
                                    │              UŻYTKOWNICY                │
                                    └───────────────────┬─────────────────────┘
                                                        │
                                                        ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                                    AZURE CLOUD                                         │
│                                                                                        │
│   ┌────────────────────────┐              ┌────────────────────────────────┐          │
│   │                        │              │                                │          │
│   │   Azure Static         │    HTTPS     │    Azure App Service           │          │
│   │   Web Apps             │─────────────►│    (Linux, Python 3.11)        │          │
│   │   (Frontend)           │              │                                │          │
│   │                        │              │    ┌──────────────────────┐    │          │
│   │   • index.html         │              │    │   Flask Application  │    │          │
│   │   • app.js             │              │    │                      │    │          │
│   │   • style.css          │              │    │   /api/events        │    │          │
│   │                        │              │    │   /api/seats         │    │          │
│   │   SKU: Free            │              │    │   /api/bookings      │    │          │
│   │                        │              │    │   /api/payments      │    │          │
│   └────────────────────────┘              │    └──────────┬───────────┘    │          │
│                                           │               │                 │          │
│                                           │    SKU: B1 (Basic)              │          │
│                                           └───────────────┬─────────────────┘          │
│                                                           │                            │
│                     ┌─────────────────────────────────────┼─────────────────────────┐  │
│                     │                                     │                         │  │
│                     ▼                                     ▼                         │  │
│   ┌────────────────────────────┐          ┌────────────────────────────────┐       │  │
│   │                            │          │                                │       │  │
│   │   Azure Key Vault          │          │   Azure SQL Database           │       │  │
│   │                            │          │                                │       │  │
│   │   Secrets:                 │          │   Tables:                      │       │  │
│   │   • SQL Connection String  │          │   • events                     │       │  │
│   │   • Stripe API Keys        │          │   • seats                      │       │  │
│   │                            │          │   • bookings                   │       │  │
│   │   SKU: Standard            │          │   • booked_seats               │       │  │
│   │                            │          │                                │       │  │
│   └────────────────────────────┘          │   SKU: Basic (5 DTU)           │       │  │
│                                           └────────────────────────────────┘       │  │
│                                                                                     │  │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│   │                                                                             │  │  │
│   │   Azure Monitor / Application Insights                                      │  │  │
│   │                                                                             │  │  │
│   │   • Request tracing          • Performance metrics                         │  │  │
│   │   • Exception logging        • Dependency tracking (SQL, Stripe)           │  │  │
│   │   • Custom events            • Alerts (Response Time, Errors, DTU)         │  │  │
│   │                                                                             │  │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │  │
│                                                                                        │
└───────────────────────────────────────────────────────────────────────────────────────┘

                                                        │
                                                        ▼
                               ┌────────────────────────────────────────┐
                               │          EXTERNAL SERVICES             │
                               │                                        │
                               │   ┌────────────────────────────────┐   │
                               │   │         Stripe API             │   │
                               │   │   (Payment Processing)         │   │
                               │   └────────────────────────────────┘   │
                               │                                        │
                               └────────────────────────────────────────┘
```

### Przepływ danych - Rezerwacja biletu

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  START   │────►│  Wybór   │────►│  Wybór   │────►│  Dane    │────►│ Płatność │
│          │     │ wydarzenia│     │  miejsc  │     │ klienta  │     │ (Stripe) │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                                         │
                                                                         ▼
                                                                   ┌──────────┐
                                                                   │Potwierdz.│
                                                                   │rezerwacji│
                                                                   └──────────┘
```

**Szczegółowy przepływ:**

1. **GET /api/events** → Użytkownik widzi listę wydarzeń
2. **GET /api/events/{id}/seats** → Pobiera mapę miejsc
3. **POST /api/bookings** → Tworzy rezerwację (status: pending)
4. **POST /api/payments/create-intent** → Tworzy Stripe PaymentIntent
5. **Stripe.js** → Przetwarza płatność po stronie klienta
6. **POST /api/payments/confirm** → Potwierdza płatność (status: paid)

---

## 3. 🔧 Usługi chmurowe

### Tabela usług

| Usługa Azure             | Rola            | Uzasadnienie wyboru                                                            |
| ------------------------ | --------------- | ------------------------------------------------------------------------------ |
| **App Service**          | Backend API     | Prosty deployment Python/Flask, automatyczne skalowanie, wbudowane logi        |
| **Static Web Apps**      | Frontend        | Darmowy hosting statycznych plików, globalny CDN, automatyczny deploy z GitHub |
| **Azure SQL Database**   | Baza danych     | Zarządzana baza relacyjna, kompatybilność z SQLAlchemy, backup automatyczny    |
| **Application Insights** | Monitoring      | Pełna observability, trace requestów, dependency tracking                      |
| **Key Vault**            | Sekrety         | Bezpieczne przechowywanie credentials, integracja z App Service                |
| **Log Analytics**        | Agregacja logów | Centralne miejsce na logi, KQL queries, retention policies                     |

### Spełnienie wymagań minimalnego zakresu technicznego:

| Wymaganie                               | Realizacja                              |
| --------------------------------------- | --------------------------------------- |
| Min. 2 usługi obliczeniowe/integracyjne | ✅ App Service + Static Web Apps        |
| Warstwa danych                          | ✅ Azure SQL Database                   |
| CI/CD                                   | ✅ GitHub Actions                       |
| Monitoring/observability                | ✅ Application Insights + Log Analytics |
| IaC                                     | ✅ Terraform                            |

---

## 4. 🔐 Konfiguracja sekretów i connection strings

### Sekrety przechowywane w Azure Key Vault:

| Sekret                  | Opis                           | Użycie      |
| ----------------------- | ------------------------------ | ----------- |
| `sql-connection-string` | Pełny connection string do SQL | Backend API |
| `stripe-secret-key`     | Klucz tajny Stripe             | Backend API |

### Zmienne środowiskowe w App Service:

```
SQL_SERVER=sql-theater-booking-xxx.database.windows.net
SQL_DATABASE=sqldb-theater-booking
SQL_USERNAME=sqladmin
SQL_PASSWORD=@Microsoft.KeyVault(SecretUri=https://kv-xxx.vault.azure.net/secrets/sql-password/)

STRIPE_SECRET_KEY=@Microsoft.KeyVault(SecretUri=https://kv-xxx.vault.azure.net/secrets/stripe-secret-key/)
STRIPE_PUBLISHABLE_KEY=pk_test_xxx

APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=xxx
```

### Bezpieczeństwo:

1. **Sekrety NIGDY nie są w kodzie** - używamy zmiennych środowiskowych
2. **Key Vault reference** - App Service pobiera sekrety bezpośrednio z Key Vault
3. **Managed Identity** (opcjonalnie) - App Service może używać managed identity
4. **.gitignore** zawiera:
   - `*.env`
   - `terraform.tfvars`
   - `*.pem`, `*.key`

### GitHub Secrets (dla CI/CD):

| Secret              | Opis                      |
| ------------------- | ------------------------- |
| `AZURE_CREDENTIALS` | JSON z Service Principal  |
| `SQL_PASSWORD`      | Hasło do bazy             |
| `STRIPE_SECRET_KEY` | Klucz Stripe              |
| `ARM_*`             | Credentials dla Terraform |

---

## 5. 💰 Koszty i limity

### Szacunkowe koszty miesięczne

| Usługa               | SKU           | Koszt USD/miesiąc | Limity                |
| -------------------- | ------------- | ----------------- | --------------------- |
| App Service Plan     | B1            | ~$13.14           | 1.75 GB RAM, 1 vCPU   |
| Azure SQL Database   | Basic         | ~$4.90            | 5 DTU, 2 GB storage   |
| Static Web Apps      | Free          | $0.00             | 100 GB bandwidth      |
| Application Insights | Pay-as-you-go | ~$2.30            | 5 GB/miesiąc included |
| Key Vault            | Standard      | ~$0.03            | 10,000 operations     |
| Log Analytics        | PerGB2018     | ~$2.30            | 5 GB/miesiąc included |
| **RAZEM**            |               | **~$22-25**       |                       |

### Optymalizacje kosztowe:

1. **Free Tier gdzie możliwe:**
   - Static Web Apps: Free
   - Application Insights: 5GB free

2. **Basic SKU dla dev/test:**
   - SQL Database Basic zamiast Standard
   - App Service B1 zamiast S1

3. **Automatyczne wyłączanie:**
   - Można skonfigurować Logic Apps do wyłączania App Service w weekendy

### Alerty kosztowe:

Zalecane ustawienie alertu budżetowego w Azure Cost Management:

- Alert przy 80% budżetu miesięcznego
- Alert przy 100% budżetu

---

## 6. 🧹 Procedura cleanup (sprzątania zasobów)

### Metoda 1: Terraform Destroy (zalecana)

```bash
cd terraform
terraform destroy
```

Terraform usunie wszystkie zasoby w odwrotnej kolejności zależności.

### Metoda 2: Azure CLI

```bash
# Usuń całą grupę zasobów (wszystko w środku)
az group delete --name rg-theater-booking --yes --no-wait
```

### Metoda 3: Portal Azure

1. Azure Portal → Resource Groups
2. Znajdź `rg-theater-booking`
3. Kliknij "Delete resource group"
4. Potwierdź wpisując nazwę grupy

### Checklist cleanup:

- [ ] `terraform destroy` wykonany
- [ ] Resource group usunięta
- [ ] Sprawdź "Deleted resources" w Azure (soft delete)
- [ ] Usuń Key Vault z "Deleted vaults" (purge)
- [ ] Usuń Service Principal (opcjonalnie):
  ```bash
  az ad sp delete --id <APP_ID>
  ```
- [ ] Usuń GitHub Secrets (jeśli repo będzie publiczne)

### UWAGA: Soft Delete

Azure SQL i Key Vault mają domyślnie włączone soft delete:

- Key Vault: 7-90 dni (konfigurowalne)
- SQL Server: 7 dni

Aby całkowicie usunąć:

```bash
# Purge deleted Key Vault
az keyvault purge --name kv-theater-booking-xxx

# SQL Server purge - automatycznie po 7 dniach
```

---

## 7. 📊 Monitoring i alerty

### Metryki monitorowane

| Metryka         | Źródło       | Próg alertu     | Uzasadnienie                             |
| --------------- | ------------ | --------------- | ---------------------------------------- |
| Response Time   | App Service  | > 3s (avg 5min) | UX - użytkownicy opuszczają wolne strony |
| HTTP 5xx Errors | App Service  | > 5 (5min)      | Krytyczne błędy serwera                  |
| DTU Usage       | SQL Database | > 80% (15min)   | Wydajność bazy danych                    |
| Failed Requests | App Insights | > 10 (5min)     | Problemy z aplikacją                     |
| Availability    | App Insights | < 99%           | SLA monitoring                           |

### Skonfigurowane alerty (w Terraform)

```hcl
# Alert: Wysoki czas odpowiedzi
resource "azurerm_monitor_metric_alert" "response_time" {
  name        = "alert-high-response-time"
  description = "Alert when average response time exceeds 3 seconds"
  severity    = 2  # Warning

  criteria {
    metric_name = "HttpResponseTime"
    aggregation = "Average"
    operator    = "GreaterThan"
    threshold   = 3
  }
}

# Alert: Błędy HTTP 5xx
resource "azurerm_monitor_metric_alert" "server_errors" {
  name        = "alert-server-errors"
  description = "Alert when HTTP 5xx errors exceed 5"
  severity    = 1  # Critical

  criteria {
    metric_name = "Http5xx"
    aggregation = "Total"
    operator    = "GreaterThan"
    threshold   = 5
  }
}

# Alert: Wykorzystanie DTU bazy
resource "azurerm_monitor_metric_alert" "db_dtu" {
  name        = "alert-database-dtu"
  description = "Alert when DTU usage exceeds 80%"
  severity    = 2  # Warning

  criteria {
    metric_name = "dtu_consumption_percent"
    aggregation = "Average"
    operator    = "GreaterThan"
    threshold   = 80
  }
}
```

### Dashboards

**Application Insights dostarcza:**

- Live Metrics Stream - dane w czasie rzeczywistym
- Application Map - mapa zależności
- Failures - analiza błędów
- Performance - analiza wydajności

### Logi

**Zbierane logi:**

- Flask application logs (INFO+)
- HTTP request/response logs
- SQL query logs (dependencies)
- Stripe API calls (dependencies)

**Przykładowe zapytanie KQL:**

```kusto
requests
| where timestamp > ago(24h)
| summarize count(), avg(duration) by name
| order by count_ desc
```

---

## 8. 🔄 CI/CD Pipeline

### Pipeline Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    PUSH     │───►│    TEST     │───►│    BUILD    │───►│   DEPLOY    │
│  to main    │    │   pytest    │    │   package   │    │   Azure     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Jobs:

1. **test** - Uruchamia pytest z coverage
2. **build-backend** - Tworzy pakiet do deploymentu
3. **deploy-backend** - Deploy na Azure App Service
4. **deploy-frontend** - Deploy na Static Web Apps
5. **terraform-plan** - Plan zmian infrastruktury (tylko PR)

### Triggery:

- `push` do `main` / `master`
- `pull_request` do `main` / `master`
- `workflow_dispatch` - ręczne uruchomienie

---

## 9. 🖥 Demo / Linki

### Działające URL:

| Komponent    | URL                                                      |
| ------------ | -------------------------------------------------------- |
| Frontend     | https://purple-river-01c768003.4.azurestaticapps.net     |
| Backend API  | https://theater-booking-api.azurewebsites.net            |
| Health Check | https://theater-booking-api.azurewebsites.net/api/health |

### Zrzuty ekranu

_(Dodaj zrzuty z:)_

1. Strony głównej z listą wydarzeń
2. Mapy miejsc
3. Formularza rezerwacji
4. Płatności Stripe
5. Potwierdzenia rezerwacji
6. Azure Portal - Application Insights dashboard
7. Azure Portal - Alerts

---

## 10. 📁 Repozytorium

### Link do repozytorium:

`https://github.com/[USERNAME]/theater-booking`

### Struktura:

```
theater-booking/
├── .github/workflows/     # CI/CD pipelines
├── backend/               # Flask API
├── frontend/              # Static files
├── terraform/             # IaC
├── docs/                  # Dokumentacja
└── README.md
```

### Historia commitów:

- Używamy konwencjonalnych commit messages
- Feature branches + Pull Requests
- Code review przed merge

---

## 11. ✅ Checklist oddania

- [ ] Repozytorium GitHub (publiczne/prywatne z dostępem)
- [ ] README z instrukcjami uruchomienia
- [ ] Pliki Terraform (IaC)
- [ ] Pipeline CI/CD (GitHub Actions)
- [ ] Dokumentacja projektu (ten plik)
- [ ] Działający URL lub nagranie demo
- [ ] Zrzuty z monitoringu
- [ ] Procedura cleanup

---

_Dokumentacja wygenerowana dla projektu Theater Booking System_
_Data: Luty 2026_
_Kurs: Cloud Computing_
