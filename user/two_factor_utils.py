from django.forms import Form
from django.shortcuts import redirect

from django_otp import devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from two_factor.forms import MethodForm, DeviceValidationForm, BackupTokenForm, AuthenticationTokenForm
from two_factor.plugins.email.method import EmailMethod
from two_factor.plugins.registry import registry
from two_factor.views import ProfileView, SetupView, LoginView

from user.forms import RememberMeAuthenticationForm


class CustomEmailMethod(EmailMethod):
    def get_setup_forms(self, wizard):
        forms = super().get_setup_forms(wizard)
        forms.pop('validation', None)
        return forms


class CustomProfileView(ProfileView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_devices = devices_for_user(self.request.user, confirmed=True)
        device_type = []
        for device in user_devices:
            if device.__class__.__name__ != 'StaticDevice':
                device_type.append(device.__class__.__name__)

        context['user_devices'] = device_type

        return context


class CustomMethodForm(MethodForm):
    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)

        available_methods = registry.get_methods()

        methods_to_exclude = set()

        if TOTPDevice.objects.filter(user=user).exists():
            methods_to_exclude.add('generator')

        if EmailDevice.objects.filter(user=user).exists():
            methods_to_exclude.add('email')

        method = self.fields['method']
        method.choices = [
            (m.code, m.verbose_name) for m in available_methods if m.code not in methods_to_exclude
        ]
        method.initial = method.choices[0][0]


class CustomLoginView(LoginView):
    AUTH_STEP = "auth"
    TOKEN_STEP = "token"
    BACKUP_STEP = "backup"
    form_list = (
        (AUTH_STEP, RememberMeAuthenticationForm),
        (TOKEN_STEP, AuthenticationTokenForm),
        (BACKUP_STEP, BackupTokenForm),
    )

    def process_step(self, form):
        result = super().process_step(form)
        if self.steps.current == self.AUTH_STEP:
            remember_me = form.cleaned_data.get('remember_me', False)
            self.request.session['remember_me'] = remember_me

        return result

    def done(self, form_list, **kwargs):
        response = super().done(form_list, **kwargs)
        self.request.session['just_logged_in'] = True

        return response


class CustomSetupView(SetupView):
    form_list = (
        ('welcome', Form),
        ('method', CustomMethodForm),
    )

    def get_method(self):
        method_data = self.storage.validated_step_data.get('method', {})
        method_key = method_data.get('method', None)
        if method_key == 'email':
            return CustomEmailMethod()
        else:
            return super().get_method()

    def get_excluded_methods(self):
        totp_is_set = TOTPDevice.objects.filter(user=self.request.user).exists()
        email_is_set = EmailDevice.objects.filter(user=self.request.user).exists()

        excluded_methods = set()

        if totp_is_set:
            excluded_methods.add('generator')

        if email_is_set:
            excluded_methods.add('email')

        return excluded_methods

    def get_available_filtered_methods(self):
        available_methods = self.get_available_methods()
        excluded_methods = self.get_excluded_methods()
        return [m for m in available_methods if m.code not in excluded_methods]

    def get(self, request, *args, **kwargs):
        available_methods = self.get_available_filtered_methods()

        if len(available_methods) == 0:
            return redirect(self.get_success_url())
        return self.render(self.get_form())

    def get_form_list(self):
        form_list = super().get_form_list()
        available_methods = self.get_available_filtered_methods()
        method = self.get_method()

        if method:
            form_list.update(method.get_setup_forms(self))
        else:
            for method in available_methods:
                form_list.update(method.get_setup_forms(self))

        return form_list
