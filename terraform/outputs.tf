# ============================================
# Outputs for Theater Booking Infrastructure
# ============================================

output "resource_group_name" {
  description = "Nazwa grupy zasobów"
  value       = azurerm_resource_group.main.name
}

output "backend_api_url" {
  description = "URL backendu API"
  value       = "https://${azurerm_linux_web_app.backend.default_hostname}"
}

output "frontend_url" {
  description = "URL frontendu"
  value       = "https://${azurerm_static_web_app.frontend.default_host_name}"
}

output "sql_server_fqdn" {
  description = "FQDN serwera SQL"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "Nazwa bazy danych"
  value       = azurerm_mssql_database.main.name
}

output "application_insights_instrumentation_key" {
  description = "Klucz instrumentacji Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "key_vault_name" {
  description = "Nazwa Key Vault"
  value       = azurerm_key_vault.main.name
}

output "static_web_app_api_key" {
  description = "Klucz API Static Web App (do deploymentu)"
  value       = azurerm_static_web_app.frontend.api_key
  sensitive   = true
}

# ============== KOSZTY SZACUNKOWE ==============

output "estimated_monthly_cost" {
  description = "Szacunkowe miesięczne koszty infrastruktury"
  value       = <<-EOT
    
    === SZACUNKOWE KOSZTY MIESIĘCZNE ===
    
    App Service Plan (B1):         ~$13.14 USD
    Azure SQL Database (Basic):    ~$4.90 USD
    Static Web App (Free):         $0.00 USD
    Application Insights:          ~$2.30 USD (do 5GB/miesiąc)
    Key Vault:                     ~$0.03 USD
    Log Analytics:                 ~$2.30 USD (do 5GB/miesiąc)
    
    RAZEM (szacunkowo):            ~$22-25 USD/miesiąc
    
    UWAGA: Koszty mogą się różnić w zależności od użycia.
    Można zminimalizować koszty używając Free Tier gdzie możliwe.
    
  EOT
}
