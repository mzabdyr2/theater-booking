# ============================================
# INSTRUKCJE ODDANIA PROJEKTU
# Theater Booking System
# ============================================

## ✅ CO JUŻ JEST GOTOWE:

1. ✅ Kod źródłowy (backend Flask + frontend)
2. ✅ Terraform IaC (terraform/)
3. ✅ GitHub Actions CI/CD (.github/workflows/)
4. ✅ Testy jednostkowe (13 testów - wszystkie przechodzą)
5. ✅ Dokumentacja (README.md + docs/ARCHITECTURE.md)
6. ✅ Monitoring (Application Insights w Terraform)
7. ✅ Bezpieczeństwo (sekrety w env vars, .gitignore)
8. ✅ Git commit gotowy

## 🔴 CO MUSISZ ZROBIĆ RĘCZNIE:

### Krok 1: Utwórz repozytorium na GitHub

1. Idź na https://github.com/new
2. Nazwa: `theater-booking`
3. Publiczne lub Prywatne (jeśli prywatne, dodaj prowadzącego)
4. NIE inicjalizuj z README (już masz)

### Krok 2: Push do GitHub

Uruchom w terminalu:

```powershell
cd C:\Python_projects\CV_projects\Ticket_reservation\theater-booking
git remote add origin https://github.com/TWOJ_USERNAME/theater-booking.git
git branch -M main
git push -u origin main
```

### Krok 3: Skonfiguruj GitHub Secrets (dla CI/CD)

GitHub → Repository → Settings → Secrets and variables → Actions

Dodaj te sekrety:
- AZURE_CREDENTIALS (JSON z Service Principal)
- AZURE_WEBAPP_NAME (np. theater-booking-api)
- AZURE_STATIC_WEB_APPS_API_TOKEN
- SQL_SERVER
- SQL_DATABASE  
- SQL_USERNAME
- SQL_PASSWORD
- STRIPE_SECRET_KEY
- STRIPE_PUBLISHABLE_KEY
- ARM_CLIENT_ID
- ARM_CLIENT_SECRET
- ARM_SUBSCRIPTION_ID
- ARM_TENANT_ID

### Krok 4: Zrób zrzuty ekranu

Zrób screenshoty z:
1. Działającej aplikacji (strona główna)
2. Mapy miejsc
3. Procesu rezerwacji
4. Azure Portal - Application Insights (metryki)
5. Azure Portal - Alerts

### Krok 5: Przygotuj paczkę do oddania

1. Link do repozytorium GitHub
2. Dokumentacja: docs/ARCHITECTURE.md (lub eksportuj do PDF)
3. Zrzuty ekranu lub link do działającej aplikacji

## 📋 PUNKTACJA - CZEGO SIĘ SPODZIEWAĆ:

| Kryterium | Max | Co masz |
|-----------|-----|---------|
| Funkcjonalność | 10 | ✅ Pełna rezerwacja + płatności |
| Architektura | 10 | ✅ 5 usług Azure, uzasadnienie |
| IaC | 5 | ✅ Terraform kompletny |
| CI/CD | 5 | ✅ GitHub Actions (test+deploy) |
| Monitoring | 5 | ✅ App Insights + 3 alerty |
| Bezpieczeństwo | 5 | ✅ Sekrety w env/KeyVault |
| Dokumentacja | 5 | ✅ README + ARCHITECTURE.md |
| Repo/higiena | 2 | ✅ .gitignore, testy |
| Operacyjność | 3 | ✅ Koszty, cleanup |
| **RAZEM** | **50** | ~45-50 pkt |

Bonus (do +10):
- Autoskalowanie - można dodać
- Dodatkowe testy - masz 13

## 🆘 PROBLEMY?

Jeśli CI/CD nie działa:
- Sprawdź GitHub Secrets
- Sprawdź logi w Actions

Jeśli Terraform nie działa:
- Sprawdź az login
- Sprawdź subscription

Powodzenia! 🎭
