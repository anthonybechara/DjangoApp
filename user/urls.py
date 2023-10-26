from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from post.views import HomeView
from . import views
from . import two_factor_utils
from .forms import EmailValidationOnForgotPassword

app_name = 'user'

urlpatterns = [

    path('', login_required(HomeView.as_view(template_name='post/index.html')), name='index'),

    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path('account/edit/', views.EditUserView.as_view(), name='edit_user'),

    path('<slug:slug>', views.UserProfile.as_view(), name='profile'),

    path('signup/', views.SignupView.as_view(), name='signup'),

    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url=reverse_lazy('user:password_change_done')),
         name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'),
         name='password_change_done'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        form_class=EmailValidationOnForgotPassword,
        template_name='registration/password_reset.html',
        success_url=reverse_lazy('user:password_reset_done')),
         name='password_reset'),

    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy("user:password_reset_complete")),
         name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    path('activate/<str:uidb64>/<str:token>/', views.ActivateUser.as_view(), name='activate_user'),

    path('activate/request_activation/', views.RequestActivation.as_view(), name='request_activation'),

    path('account/login/', two_factor_utils.CustomLoginView.as_view(), name='login'),

    path('account/two_factor/', two_factor_utils.CustomProfileView.as_view(), name='2fa_security'),

    path('account/two_factor/setup/', two_factor_utils.CustomSetupView.as_view(), name='2fa_setup'),

    path('account/two_factor/disable/', views.SecurityPage.as_view(), name='2fa_disable'),

    path('account/two_factor/disable/totp/<int:pk>/', views.DisableTOTP.as_view(), name='totp_disable'),

    path('account/two_factor/disable/static/<int:pk>/', views.DisableStatic.as_view(), name='static_disable'),

    path('account/two_factor/disable/email/<int:pk>/', views.DisableEmail.as_view(), name='email_disable'),

]
