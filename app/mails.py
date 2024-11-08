from mailersend import emails
from app.core.config import settings


# Inicializar el cliente de correo
mailer = emails.NewEmail(settings.MAILERSEND_API_KEY)

# Diccionario de templates
TEMPLATES = {
    "password_reset": "3z0vklow8m747qrx",
}

def send_email(template_key, recipients, personalization_data, subject):
    """
    Envía un correo usando MailerSend con el template y personalización especificados.

    Args:
        template_key (str): Clave para seleccionar el template del diccionario TEMPLATES.
        recipients (list): Lista de destinatarios con formato [{"name": "Nombre", "email": "email@dominio.com"}].
        personalization_data (list): Lista de personalización en formato [{"email": "email@dominio.com", "data": {...}}].
        subject (str): Asunto del correo.
    """
    mail_body = {}
    mail_from = {
        "name": "Fintech API",
        "email": settings.MAILERSEND_SENDER,
    }

    # Validar si el template_key existe en el diccionario de templates
    template_id = TEMPLATES.get(template_key)
    if not template_id:
        raise ValueError(f"Template '{template_key}' no encontrado en el diccionario de templates.")

    # Configurar los parámetros del correo
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_template(template_id, mail_body)
    mailer.set_personalization(personalization_data, mail_body)

    # Enviar el correo
    mailer.send(mail_body)

