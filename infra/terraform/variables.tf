variable "presenter_cidr" {
  description = "IPv4 pública del presentador, exclusivamente /32. No es un secreto."
  type        = string
  validation {
    condition     = can(cidrnetmask(var.presenter_cidr)) && endswith(var.presenter_cidr, "/32")
    error_message = "Usar una IPv4 válida con máscara /32."
  }
}

variable "image_tag" {
  description = "Etiqueta inmutable que se publicará en ECR antes de arrancar tareas."
  type        = string
  validation {
    condition     = can(regex("^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$", var.image_tag)) && var.image_tag != "latest"
    error_message = "Usar una etiqueta explícita válida, distinta de latest."
  }
}

variable "desired_count" {
  description = "Preparación de infraestructura: mantener cero hasta completar el arranque cloud."
  type        = number
  default     = 0
  validation {
    condition     = var.desired_count == 0
    error_message = "Esta etapa solo permite cero tareas. Resolver primero publicación, secreto y espera de Atlas en T43."
  }
}

variable "mongodb_database" {
  description = "Nombre de la base Atlas ya preparada; no se inicializa desde Terraform."
  type        = string
  default     = "delivery"
  validation {
    condition     = can(regex("^[A-Za-z0-9_-]+$", var.mongodb_database))
    error_message = "Indicar un nombre de base válido."
  }
}
