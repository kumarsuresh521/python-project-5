'''
Email reusable component


'''

from app.models import EmailMessage
from django.conf import settings
from django.core.mail import EmailMessage as DjangoMail
from django.template.loader import get_template

from .tasks import send_email


class Email(object):
    ''' Email
    Email class create an instance of Email
    with messages with sender and receiver information
    in EmailMessage'''

    def __init__(self, to_email, subject, html_msg=None, carbon_copy=None, from_addr=None):
        '''init'''
        self.to_email = to_email
        self.subject = subject
        self.html_msg = html_msg
        self.carbon_copy = carbon_copy
        self.from_addr = from_addr

    def html_message(self, html_message):
        ''' Html object 
        set html_message in instance'''
        self.html_msg = html_message
        return self

    def from_address(self, from_address):
        '''set email
        address of sender
        in from_addr field
        '''
        self.from_addr = from_address
        return self

    def message_from_template(self, template_name, context, request=None):
        ''' Message Body
        it integrate the message with template'''
        self.html_msg = get_template(
            template_name).render(context, request)
        return self

    def send(self):
        ''' Create object of instance of Email and 
        save in EmailMessage '''
        if not self.from_addr:
            self.from_addr = settings.EMAIL_DEFAULT
        if not self.html_msg:
            raise Exception('You must provide a text or html body.')
        email_data = {
            'from_email': self.from_addr,
            'to_email': self.to_email,
            'cc': self.carbon_copy,
            'subject': self.subject,
            'html_message': self.html_msg

        }
        email_obj = EmailMessage.objects.create(**email_data)
        try:
            if not eval(settings.CELERY_ENABLED):
                email = DjangoMail(self.subject, self.html_msg,
                                   self.from_addr, to=[self.to_email, ])
                email.content_subtype = "html"
                email.send()
                email_obj.status = EmailMessage.SENT
                email_obj.save()
            else:
                send_email.delay(email_obj.pk)
        except ValueError:
            pass
