# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import forms as authforms
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail.message import EmailMultiAlternatives
from django.template import loader
from django.template.context import Context
from django.utils.http import int_to_base36

import settings


class LoginForm(forms.Form):
	email = forms.EmailField(error_messages={'invalid': 'Enter your email', 'required': 'This field is mandatory'}, label='E-mail')
	password = forms.CharField(error_messages={'required': 'Enter your password'}, max_length=128, label='Password', widget=forms.PasswordInput)


	def __init__(self, request=None, *args, **kwargs):
		self.request = request
		self.authenticated_user = None
		super(LoginForm, self).__init__(*args, **kwargs)


	def clean(self):
		if self.request:
			if not self.request.session.test_cookie_worked():
				raise forms.ValidationError('Your browser doesn\'t have cookies enabled. Please enable them so that the application can work correctly')

		email = self.cleaned_data.get("email")
		password = self.cleaned_data.get("password")

		if email and password:
			user = User.objects.filter(email__iexact=email)
			if user.count():
				self.authenticated_user = authenticate(username=user[0].username, password=password)
				if self.authenticated_user is None:
					raise forms.ValidationError('Email and password don\'t match.')
				elif not self.authenticated_user.is_active:
					raise forms.ValidationError('User account isn\'t active')
			else:
				raise forms.ValidationError('Email and password don\'t match.')

		return self.cleaned_data


	def get_user(self):
		return self.authenticated_user


class PasswordResetForm(authforms.PasswordResetForm):
	def save(self, from_email, domain_override=None, email_template_name='registration/password_reset_email.html', use_https=False, token_generator=default_token_generator, request=None):
		try:
			user = User.objects.get(email=self.cleaned_data['email'])
			site = Site.objects.get(name='TicketTracker')
		except Exception, e:
			raise ValidationError(e)

		ctx = Context({'email': user.email, 'domain': site.domain, 'site_name': site.name, 'uid': int_to_base36(user.id), 'user': user, 'token': token_generator.make_token(user), 'protocol': use_https and 'https' or 'http', })

		text_body = loader.get_template('email/email_password_reset.txt').render(ctx)
		html_body = loader.get_template('email/email_password_reset.html').render(ctx)
		try:
			bcc = []
			if hasattr(settings, 'EMAIL_LOG'):
				bcc.append(settings.EMAIL_LOG)
			email = EmailMultiAlternatives('Password reset for TicketTracker', text_body, settings.SERVER_EMAIL, [user.email], bcc)
			email.attach_alternative(html_body, 'text/html')
			email.send()
		except Exception, ex:
			pass # TODO: do something when SMTP fails, but do not draw an error page


class SetPasswordForm(authforms.SetPasswordForm):
	new_password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
	new_password2 = forms.CharField(label="Password repeated", widget=forms.PasswordInput)
