import pytest
from unittest.mock import patch
from app.mails import send_email, mailer


@pytest.fixture
def mock_mailer():
    with patch.object(mailer, 'set_mail_from') as mock_set_mail_from, \
            patch.object(mailer, 'set_mail_to') as mock_set_mail_to, \
            patch.object(mailer, 'set_subject') as mock_set_subject, \
            patch.object(mailer, 'set_template') as mock_set_template, \
            patch.object(mailer, 'set_personalization') as mock_set_personalization, \
            patch.object(mailer, 'send') as mock_send:
        yield {
            'set_mail_from': mock_set_mail_from,
            'set_mail_to': mock_set_mail_to,
            'set_subject': mock_set_subject,
            'set_template': mock_set_template,
            'set_personalization': mock_set_personalization,
            'send': mock_send,
        }


def test_send_email_success(mock_mailer):
    template_key = "password_reset"
    recipients = [{"name": "John Doe", "email": "john.doe@example.com"}]
    personalization_data = [
        {"email": "john.doe@example.com", "data": {"name": "John"}}]
    subject = "Password Reset"

    send_email(template_key, recipients, personalization_data, subject)

    assert mock_mailer['set_mail_from'].called
    assert mock_mailer['set_mail_to'].called
    assert mock_mailer['set_subject'].called
    assert mock_mailer['set_template'].called
    assert mock_mailer['set_personalization'].called
    assert mock_mailer['send'].called


def test_send_email_failure(mock_mailer):
    mock_mailer['send'].side_effect = Exception("Sendgrid Error")

    with pytest.raises(Exception, match="Sendgrid Error"):
        send_email("password_reset", [{"name": "John Doe", "email": "john.doe@example.com"}], [
                   {"email": "john.doe@example.com", "data": {"name": "John"}}], "Password Reset")


def test_send_email_template_not_found(mock_mailer):
    template_key = "nonexistent_template"
    with pytest.raises(Exception, match=f"Template '{template_key}' no encontrado en el diccionario de templates."):
        send_email(template_key, [{"name": "John Doe", "email": "john.doe@example.com"}], [
                   {"email": "john.doe@example.com", "data": {"name": "John"}}], "Password Reset")
