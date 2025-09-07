from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_invoice_email(subject, message, recipient_list, context):
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )
    html_content = render_to_string("factures.html", context)
    email.attach_alternative(html_content, "text/html")
    email.send()
    return True
