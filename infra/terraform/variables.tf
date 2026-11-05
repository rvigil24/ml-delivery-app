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
  description = "Cero por defecto; uno solo tras autorizar despliegue y preparar imagen/secreto."
  type        = number
  default     = 0
  validation {
    condition     = contains([0, 1], var.desired_count)
    error_message = "La demo permite cero o una tarea."
  }
}

variable "start_timeout_seconds" {
  description = "Espera de Atlas en segundos; cero espera sin límite evitando rotación de IP por timeout."
  type        = number
  default     = 900
  validation {
    condition     = var.start_timeout_seconds >= 0 && var.start_timeout_seconds <= 3600 && floor(var.start_timeout_seconds) == var.start_timeout_seconds
    error_message = "Indicar cero (sin límite) o un entero entre 1 y 3600 segundos."
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


variable "public_api_access" {
  description = "Permitir HTTP público para el proxy Vercel de la demo; requiere autorización explícita."
  type        = bool
  default     = false
}

variable "demo_enabled" {
  description = "Habilitar los escenarios simulados completos en la API desplegada."
  type        = bool
  default     = false
}
