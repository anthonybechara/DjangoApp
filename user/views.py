from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView, TemplateView
from django.views import View
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from .models import User
from .forms import CustomUserCreationForm, EditUser
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_email.models import EmailDevice


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        session_identifier = str(request.session.get('unique_session_id'))

        if session_identifier:
            for key in list(request.session.keys()):
                if session_identifier in key:
                    del request.session[key]

        return super().dispatch(request, *args, **kwargs)


class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'registration/profile.html'


class EditUserView(LoginRequiredMixin, View):
    template_name = 'registration/edit_user.html'

    def get(self, request, *args, **kwargs):
        user_form = EditUser(instance=request.user)
        return render(request, self.template_name, {'user_form': user_form})

    def post(self, request, *args, **kwargs):
        user_form = EditUser(instance=request.user, data=request.POST, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            return redirect(reverse('user:profile', kwargs={'slug': request.user.slug}))

        return render(request, self.template_name, {'user_form': user_form})


class SignupView(CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save()
        self.send_activation_email(user)
        messages.success(self.request, 'Registration Done.', extra_tags='success')
        return render(self.request, 'registration/registered_user.html', {'user_name': user.first_name})

    def send_activation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        current_site = get_current_site(self.request)
        activation_link = f'http://{current_site.domain}/activate/{uid}/{token}/'

        subject = 'Activate Your Account'
        message = f'To activate your account, please click the following link:\n{activation_link}'
        recipient_list = [user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


class ActivateUser(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated. You can now log in.', extra_tags='success')
        else:
            messages.error(request, 'Invalid activation link. Please contact support.', extra_tags='error')

        return redirect(reverse_lazy('user:login'))


class RequestActivation(View):
    template_name = 'registration/request_activation.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            user = None

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            current_site = get_current_site(request)
            activation_link = f'http://{current_site.domain}/activate/{uid}/{token}/'

            subject = 'Activate Your Account'
            message = f'To activate your account, please click the following link:\n{activation_link}'
            recipient_list = [user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

            messages.success(request, 'A new activation link has been sent to your email. Please check your inbox.',
                             extra_tags='success')
            return redirect(reverse_lazy('user:login'))
        else:
            messages.error(request, 'No inactive user found with the provided email address.', extra_tags='error-mail')
            return render(request, self.template_name)


class SecurityPage(LoginRequiredMixin, TemplateView):
    template_name = 'two_factor/security.html'

    def get(self, request, *args, **kwargs):
        totp_devices = TOTPDevice.objects.filter(user=self.request.user)
        email_devices = EmailDevice.objects.filter(user=self.request.user)
        if not (totp_devices.exists() or email_devices.exists()):
            return redirect(reverse('user:2fa_security'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        totp_devices = TOTPDevice.objects.filter(user=self.request.user)
        static_devices = StaticDevice.objects.filter(user=self.request.user)
        email_devices = EmailDevice.objects.filter(user=self.request.user)
        context['totp_devices'] = totp_devices
        context['static_devices'] = static_devices
        context['email_devices'] = email_devices

        return context


class DisableTOTP(LoginRequiredMixin, DeleteView):
    model = TOTPDevice
    success_url = reverse_lazy('user:2fa_security')

    def get_object(self, queryset=None):
        return get_object_or_404(TOTPDevice, user=self.kwargs['pk'])


class DisableEmail(LoginRequiredMixin, DeleteView):
    model = EmailDevice
    success_url = reverse_lazy('user:2fa_security')

    def get_object(self, queryset=None):
        return get_object_or_404(EmailDevice, user=self.kwargs['pk'])


class DisableStatic(LoginRequiredMixin, DeleteView):
    model = StaticDevice
    success_url = reverse_lazy('user:2fa_security')

    def get_object(self, queryset=None):
        return get_object_or_404(StaticDevice, user=self.kwargs['pk'])
