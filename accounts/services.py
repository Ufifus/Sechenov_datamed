from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.conf import settings

import six


def get_action_email(request, user):
    current_site = get_current_site(request)
    email_message = 'Verify your account'
    email_body = render_to_string('accounts/activate_user.html',{
        'user': user,
        'domain': current_site,
        'uid64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user)
    })
    print(email_body)
    email = EmailMessage(subject=email_message, body=email_body,
                 from_email=settings.EMAIL_HOST_USER,
                 to=[user.email])
    email.send()
    print('success')


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)


token_generator = TokenGenerator()