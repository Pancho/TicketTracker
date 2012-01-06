from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import settings

from web import forms

urlpatterns = patterns('',
	# web
    (r'^', include('web.urls')),

    # Static serving
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),

    # Django admin
    (r'^admin/', include(admin.site.urls)),
)

#Auth
urlpatterns += patterns('django.contrib.auth.views',
	url(r'^logout$', 'logout_then_login', name='logout'),

	url(r'^password/reset$', 'password_reset', {'password_reset_form': forms.PasswordResetForm, 'template_name': 'pages/password_reset.html'}, name='password_reset'),
	url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$', 'password_reset_confirm', {'set_password_form': forms.SetPasswordForm, 'template_name': 'pages/password_reset_confirm.html'}, name='password_reset_confirm'),
	url(r'^password/reset/done$', 'password_reset_complete', {'template_name': 'pages/password_reset_complete.html'}, name='standalone_password_reset_complete'),
	url(r'^password/reset/sent$', 'password_reset_done', {'template_name': 'pages/password_reset_done.html'}, name='standalone_password_reset_done'),
)