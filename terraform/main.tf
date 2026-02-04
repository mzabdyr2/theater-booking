# ============================================
# Theater Booking System - Azure Infrastructure
# ============================================
# Usługi:
# - Azure App Service (Web App) - Backend API (Python/Flask)
# - Azure Static Web App - Frontend (HTML/CSS/JS)
# - Azure SQL Database - Baza danych
# - Azure Application Insights - Monitoring
# - Azure Key Vault - Sekrety
# ============================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

# ============== DATA SOURCES ==============

data "azurerm_client_config" "current" {}

# ============== RESOURCE GROUP ==============

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = var.tags
}

# ============== RANDOM SUFFIX ==============

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# ============== LOG ANALYTICS WORKSPACE ==============

resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = var.tags
}

# ============== APPLICATION INSIGHTS ==============

resource "azurerm_application_insights" "main" {
  name                = "appi-${var.project_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = var.tags
}

# ============== KEY VAULT ==============

resource "azurerm_key_vault" "main" {
  name                        = "kv-${var.project_name}-${random_string.suffix.result}"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = false
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }

  tags = var.tags
}

# ============== SQL SERVER ==============

resource "azurerm_mssql_server" "main" {
  name                         = "sql-${var.project_name}-${random_string.suffix.result}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"

  tags = var.tags
}

# ============== SQL DATABASE ==============

resource "azurerm_mssql_database" "main" {
  name                        = "sqldb-${var.project_name}"
  server_id                   = azurerm_mssql_server.main.id
  collation                   = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb                 = 2
  sku_name                    = "Basic"
  zone_redundant              = false
  auto_pause_delay_in_minutes = -1

  tags = var.tags
}

# ============== SQL FIREWALL RULE - Azure Services ==============

resource "azurerm_mssql_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# ============== APP SERVICE PLAN ==============

resource "azurerm_service_plan" "main" {
  name                = "asp-${var.project_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"

  tags = var.tags
}

# ============== APP SERVICE - BACKEND API ==============

resource "azurerm_linux_web_app" "backend" {
  name                = "app-${var.project_name}-api-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true

  site_config {
    always_on = true
    
    application_stack {
      python_version = "3.11"
    }

    cors {
      allowed_origins = ["*"]
    }
  }

  app_settings = {
    "SCM_DO_BUILD_DURING_DEPLOYMENT"    = "true"
    "ENABLE_ORYX_BUILD"                 = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    
    # Database connection
    "SQL_SERVER"   = azurerm_mssql_server.main.fully_qualified_domain_name
    "SQL_DATABASE" = azurerm_mssql_database.main.name
    "SQL_USERNAME" = var.sql_admin_username
    "SQL_PASSWORD" = var.sql_admin_password
    
    # Stripe (from variables)
    "STRIPE_SECRET_KEY"      = var.stripe_secret_key
    "STRIPE_PUBLISHABLE_KEY" = var.stripe_publishable_key
    
    # Application Insights
    "APPINSIGHTS_INSTRUMENTATIONKEY"        = azurerm_application_insights.main.instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main.connection_string
    
    # Flask settings
    "FLASK_ENV" = "production"
    "SECRET_KEY" = random_string.flask_secret.result
  }

  logs {
    application_logs {
      file_system_level = "Information"
    }
    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
  }

  tags = var.tags
}

resource "random_string" "flask_secret" {
  length  = 32
  special = true
}

# ============== STATIC WEB APP - FRONTEND ==============

resource "azurerm_static_web_app" "frontend" {
  name                = "stapp-${var.project_name}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = "westeurope"
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = var.tags
}

# ============== KEY VAULT SECRETS ==============

resource "azurerm_key_vault_secret" "sql_connection" {
  name         = "sql-connection-string"
  value        = "Server=${azurerm_mssql_server.main.fully_qualified_domain_name};Database=${azurerm_mssql_database.main.name};User Id=${var.sql_admin_username};Password=${var.sql_admin_password};"
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "stripe_secret" {
  name         = "stripe-secret-key"
  value        = var.stripe_secret_key
  key_vault_id = azurerm_key_vault.main.id
}

# ============== MONITORING ALERTS ==============

# Alert: High Response Time
resource "azurerm_monitor_metric_alert" "response_time" {
  name                = "alert-high-response-time"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_linux_web_app.backend.id]
  description         = "Alert when average response time exceeds 3 seconds"
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "HttpResponseTime"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 3
  }

  tags = var.tags
}

# Alert: HTTP 5xx Errors
resource "azurerm_monitor_metric_alert" "server_errors" {
  name                = "alert-server-errors"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_linux_web_app.backend.id]
  description         = "Alert when HTTP 5xx errors exceed 5 in 5 minutes"
  severity            = 1
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  tags = var.tags
}

# Alert: Database DTU Usage
resource "azurerm_monitor_metric_alert" "db_dtu" {
  name                = "alert-database-dtu"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_mssql_database.main.id]
  description         = "Alert when database DTU usage exceeds 80%"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.Sql/servers/databases"
    metric_name      = "dtu_consumption_percent"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }

  tags = var.tags
}
