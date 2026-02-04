# 🎭 Theater Booking System

System rezerwacji biletów do teatru zbudowany w architekturze chmurowej na platformie Microsoft Azure.

## 📋 Spis treści

- [Opis projektu](#-opis-projektu)
- [Architektura](#-architektura)
- [Technologie](#-technologie)
- [Uruchomienie lokalne](#-uruchomienie-lokalne)
- [Deployment w chmurze](#-deployment-w-chmurze)
- [CI/CD](#-cicd)
- [Monitoring](#-monitoring)
- [Struktura projektu](#-struktura-projektu)
- [API Documentation](#-api-documentation)
- [Koszty](#-koszty)
- [Cleanup](#-cleanup)

## 📖 Opis projektu

Theater Booking System to aplikacja webowa umożliwiająca:

- Przeglądanie dostępnych wydarzeń teatralnych
- Interaktywny wybór miejsc na sali
- Rezerwację biletów online
- Płatności online przez Stripe (demo dla testów)

### Główne funkcje:

- 🎫 Rezerwacja biletów na wydarzenia teatralne (obecnie 1)
- 💺 Interaktywna mapa miejsc z kategoriami (VIP, Standard, Economy)
- 💳 Bezpieczne płatności online (Stripe)
- 📧 Potwierdzenie rezerwacji z numerem referencyjnym

## 🏗 Architektura

```
┌─────────────────────────────────────────────────────────────────┐
│                         AZURE CLOUD                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────┐         ┌──────────────────────────┐    │
│   │  Static Web App  │         │     App Service (B1)     │    │
│   │    (Frontend)    │ ──────► │    Backend API (Flask)   │    │
│   │   HTML/CSS/JS    │         │      Python 3.11         │    │
│   └──────────────────┘         └────────────┬─────────────┘    │
│                                              │                   │
│                                              ▼                   │
│   ┌──────────────────┐         ┌──────────────────────────┐    │
│   │   Key Vault      │         │    Azure SQL Database    │    │
│   │   (Secrets)      │◄────────│        (Basic)           │    │
│   └──────────────────┘         └──────────────────────────┘    │
│                                                                  │
│   ┌──────────────────────────────────────────────────────┐     │
│   │              Application Insights                     │     │
│   │         (Monitoring, Logs, Alerts)                   │     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

External Services:
┌──────────────┐
│   Stripe     │  (Payment processing)
└──────────────┘
```

### Usługi Azure:

| Usługa                   | Przeznaczenie           | SKU/Tier      |
| ------------------------ | ----------------------- | ------------- |
| **App Service**          | Backend API (Flask)     | B1 (Basic)    |
| **Static Web Apps**      | Frontend (HTML/CSS/JS)  | Free          |
| **Azure SQL Database**   | Baza danych             | Basic (5 DTU) |
| **Application Insights** | Monitoring i logi       | Pay-as-you-go |
| **Key Vault**            | Przechowywanie sekretów | Standard      |
| **Log Analytics**        | Agregacja logów         | PerGB2018     |

## 🛠 Technologie

### Backend:

- Python 3.11
- Flask 2.3
- SQLAlchemy 2.0
- Azure SQL Database (MS SQL)
- Stripe SDK

### Frontend:

- HTML5, CSS3, JavaScript (Vanilla)
- Stripe.js

### Infrastructure:

- Terraform (IaC)
- GitHub Actions (CI/CD)
- Azure Application Insights (Monitoring)

## 🚀 Uruchomienie lokalne

### Wymagania:

- Python 3.11+
- Git

### Kroki:

1. **Sklonuj repozytorium:**

```bash
git clone https://github.com/YOUR_USERNAME/theater-booking.git
cd theater-booking
```

2. **Utwórz środowisko wirtualne:**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Zainstaluj zależności:**

```bash
pip install -r requirements.txt
```

4. **Skonfiguruj zmienne środowiskowe:**

```bash
# Skopiuj przykładowy plik
cp .env.example .env

# Edytuj .env i uzupełnij wartości
```

Zawartość `.env`:

```env
# Dla uruchomienia lokalnego (SQLite)
# Pozostaw puste - użyje SQLite automatycznie
SQL_SERVER=
SQL_DATABASE=
SQL_USERNAME=
SQL_PASSWORD=

# Stripe (opcjonalne dla testów)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Flask
SECRET_KEY=your-secret-key-here
```

5. **Uruchom backend:**

```bash
python app.py
```

Backend będzie dostępny na: `http://localhost:8000`

6. **Uruchom frontend:**

```bash
# W nowym terminalu, z katalogu frontend/
# Można użyć dowolnego serwera HTTP

# Python
python -m http.server 3000

# Lub VS Code Live Server
```

Frontend będzie dostępny na: `http://localhost:3000`

7. **Zainicjalizuj bazę danych:**

```bash
# Otwórz w przeglądarce lub użyj curl
curl -X POST http://localhost:8000/api/init-db
```

### Uruchomienie testów:

```bash
cd backend
pytest tests/ -v
```

## ☁️ Deployment w chmurze

### Wymagania:

- Konto Azure
- Azure CLI zainstalowane
- Terraform 1.0+

### Krok 1: Zaloguj się do Azure

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### Krok 2: Skonfiguruj Terraform

```bash
cd terraform

# Skopiuj przykładowy plik zmiennych
cp terraform.tfvars.example terraform.tfvars

# Edytuj terraform.tfvars i uzupełnij wartości
```

### Krok 3: Deploy infrastruktury

```bash
terraform init
terraform plan
terraform apply
```

### Krok 4: Deploy aplikacji

**Backend:**

```bash
cd backend
az webapp up --name YOUR_WEBAPP_NAME --resource-group rg-theater-booking
```

**Frontend:**
Frontend deployuje się automatycznie przez GitHub Actions po pushu do `main`.

### Krok 5: Konfiguracja GitHub Secrets

Dodaj następujące sekrety w GitHub Repository → Settings → Secrets:

| Secret Name                       | Opis                      |
| --------------------------------- | ------------------------- |
| `AZURE_CREDENTIALS`               | Service Principal JSON    |
| `AZURE_WEBAPP_NAME`               | Nazwa App Service         |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token dla Static Web Apps |
| `SQL_SERVER`                      | FQDN serwera SQL          |
| `SQL_DATABASE`                    | Nazwa bazy danych         |
| `SQL_USERNAME`                    | Login SQL                 |
| `SQL_PASSWORD`                    | Hasło SQL                 |
| `STRIPE_SECRET_KEY`               | Klucz tajny Stripe        |
| `STRIPE_PUBLISHABLE_KEY`          | Klucz publiczny Stripe    |
| `ARM_CLIENT_ID`                   | Azure Service Principal   |
| `ARM_CLIENT_SECRET`               | Azure Service Principal   |
| `ARM_SUBSCRIPTION_ID`             | ID subskrypcji Azure      |
| `ARM_TENANT_ID`                   | ID tenanta Azure          |

#### Tworzenie Service Principal:

```bash
az ad sp create-for-rbac --name "theater-booking-sp" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

## 🔄 CI/CD

Pipeline CI/CD w GitHub Actions wykonuje:

1. **Test** - uruchamia testy jednostkowe (pytest)
2. **Build** - buduje pakiet deploymentu
3. **Deploy Backend** - deployuje na Azure App Service
4. **Deploy Frontend** - deployuje na Azure Static Web Apps

### Workflowy:

- `.github/workflows/ci-cd.yml` - główny pipeline (push do main)
- `.github/workflows/terraform.yml` - deployment infrastruktury (ręczny)

## 📊 Monitoring

### Application Insights monitoruje:

- **Metryki aplikacji:**
  - Czas odpowiedzi (Response Time)
  - Liczba requestów
  - Błędy HTTP 4xx/5xx
  - Zależności (SQL, Stripe)

- **Logi:**
  - Logi aplikacji Flask
  - Logi HTTP requests
  - Błędy i wyjątki

### Skonfigurowane alerty:

| Alert              | Warunek              | Severity |
| ------------------ | -------------------- | -------- |
| High Response Time | Avg > 3s (5 min)     | Warning  |
| Server Errors      | HTTP 5xx > 5 (5 min) | Critical |
| Database DTU       | DTU > 80% (15 min)   | Warning  |

### Dostęp do monitoringu:

1. Azure Portal → Application Insights
2. Zakładka "Live Metrics" - dane w czasie rzeczywistym
3. Zakładka "Failures" - analiza błędów
4. Zakładka "Performance" - analiza wydajności

## 📁 Struktura projektu

```
theater-booking/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml           # Pipeline CI/CD
│       └── terraform.yml       # Deploy infrastruktury
├── backend/
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py         # Testy jednostkowe
│   ├── app.py                  # Główna aplikacja Flask
│   ├── config.py               # Konfiguracja
│   ├── models.py               # Modele SQLAlchemy
│   ├── requirements.txt        # Zależności Python
│   └── pytest.ini              # Konfiguracja pytest
├── frontend/
│   ├── css/
│   │   └── style.css           # Style CSS
│   ├── js/
│   │   └── app.js              # Logika JavaScript
│   └── index.html              # Strona główna
├── terraform/
│   ├── main.tf                 # Definicja infrastruktury
│   ├── variables.tf            # Zmienne
│   ├── outputs.tf              # Outputy
│   └── terraform.tfvars.example
├── docs/
│   └── ARCHITECTURE.md         # Dokumentacja architektury
├── README.md                   # Ten plik
└── requirements.txt            # Zależności (root)
```

## 📡 API Documentation

### Endpoints:

#### Health Check

```
GET /                    # Status aplikacji
GET /api/health          # Health check
```

#### Events

```
GET /api/events          # Lista wydarzeń
GET /api/events/:id      # Szczegóły wydarzenia
```

#### Seats

```
GET /api/events/:id/seats    # Mapa miejsc
```

#### Bookings

```
POST /api/bookings       # Utwórz rezerwację
```

#### Payments

```
POST /api/payments/create-intent    # Utwórz Stripe PaymentIntent
POST /api/payments/confirm          # Potwierdź płatność
```

#### Admin

```
POST /api/init-db        # Inicjalizuj bazę danych
```

### Przykład rezerwacji:

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "seat_ids": [1, 2, 3],
    "customer_name": "Jan Kowalski",
    "customer_email": "jan@example.com",
    "customer_phone": "+48123456789"
  }'
```

## 💰 Koszty

### Szacunkowe koszty miesięczne (Azure):

| Usługa               | SKU      | Koszt/miesiąc   |
| -------------------- | -------- | --------------- |
| App Service Plan     | B1       | ~$13 USD        |
| Azure SQL Database   | Basic    | ~$5 USD         |
| Static Web Apps      | Free     | $0              |
| Application Insights | 5GB      | ~$2-3 USD       |
| Key Vault            | Standard | ~$0.03 USD      |
| Log Analytics        | 5GB      | ~$2-3 USD       |
| **RAZEM**            |          | **~$22-25 USD** |

### Optymalizacja kosztów:

- Używaj Free Tier gdzie możliwe
- Ustaw limity na Application Insights
- Rozważ wyłączenie usług w weekendy (dev/test)

## 🧹 Cleanup

### Usunięcie zasobów przez Terraform:

```bash
cd terraform
terraform destroy
```

### Ręczne usunięcie (Azure CLI):

```bash
# Usuń całą grupę zasobów
az group delete --name rg-theater-booking --yes --no-wait
```

### Cleanup checklist:

- [ ] Terraform destroy
- [ ] Sprawdź czy grupa zasobów usunięta
- [ ] Usuń Service Principal (opcjonalnie)
- [ ] Usuń GitHub Secrets (opcjonalnie)

## 👥 Autorzy

- Maciej Zabdyr, Filip Przyczyna
- Kurs: Obliczenia w chmurze, Semestr zimowy 2025/2026

## 📄 Licencja

MIT License - zobacz plik [LICENSE](LICENSE)
