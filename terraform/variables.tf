# ============================================
# Variables for Theater Booking Infrastructure
# ============================================

variable "project_name" {
  description = "Nazwa projektu (używana w nazwach zasobów)"
  type        = string
  default     = "theater-booking"
}

variable "location" {
  description = "Region Azure dla zasobów"
  type        = string
  default     = "westeurope"
}

variable "resource_group_name" {
  description = "Nazwa grupy zasobów"
  type        = string
  default     = "rg-theater-booking"
}

variable "sql_admin_username" {
  description = "Nazwa administratora SQL Server"
  type        = string
  default     = "sqladmin"
}

variable "sql_admin_password" {
  description = "Hasło administratora SQL Server"
  type        = string
  sensitive   = true
}

variable "stripe_secret_key" {
  description = "Klucz tajny Stripe (SK)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_publishable_key" {
  description = "Klucz publiczny Stripe (PK)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tagi dla zasobów"
  type        = map(string)
  default = {
    Project     = "Theater Booking"
    Environment = "Production"
    ManagedBy   = "Terraform"
    Course      = "Cloud Computing"
  }
}
