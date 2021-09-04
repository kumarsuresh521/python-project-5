'''
Register Celery Task
'''
# pylint: disable=w0612
from smtplib import SMTPException

from app.models import EmailMessage
from celery import shared_task, task
from django.core.mail import EmailMessage as DjangoMail


@shared_task(bind=True, max_retries=3)
def send_email(self, email_id):
    '''
    Send Email
    '''
    data = {}
    try:
        email_obj = EmailMessage.objects.get(pk=email_id)
        data = {'email': email_obj.to_email,
                'from_email': email_obj.from_email,
                'subject': email_obj.subject}
        email = DjangoMail(email_obj.subject, email_obj.html_message,
                           email_obj.from_email, to=[email_obj.to_email, ])
        email.content_subtype = "html"
        email.send()
        email_obj.sent_status = EmailMessage.SENT
        email_obj.save()
        data['result'] = 'success'
    except SMTPException as exc:
        data['result'] = 'failed'
        data['error_message'] = 'error'
        self.retry(exc=exc, countdown=180)
    except EmailMessage.DoesNotExist as exc:
        data['result'] = 'failed'
        data['error_message'] = email_id
        self.retry(exc=exc, countdown=30)
    return data
