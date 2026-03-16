from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from voters.views import home_view

# Customize admin site headers
admin.site.site_header = 'ELECTRA Administration'
admin.site.site_title = 'ELECTRA Admin'
admin.site.index_title = 'Welcome to ELECTRA Administration'

urlpatterns = [
    # Home Page
    path('', home_view, name='home'),

    # App URLs
    path('accounts/', include('accounts.urls')),
    path('elections/', include('elections.urls')),
    path('contestants/', include('contestants.urls')),
    path('votes/', include('votes.urls')),
    path('', include('voters.urls')),

    # Django Admin
    path('admin/', admin.site.urls),

    # Password Reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

# Serve static and media files
# In production, Nginx/Apache will serve these, but Django can handle it as backup
if settings.DEBUG:
    # Development: Django serves static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: Still add these for fallback (Nginx will handle most requests)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)