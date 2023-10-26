from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField, PasswordResetForm, \
    AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User
from captcha.fields import ReCaptchaField


class RememberMeAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


class EditUser(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'middle_name', 'birth_date', 'gender',
                  'country', 'city', 'photo']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            min_date = timezone.now().date() - timedelta(days=15 * 365)  # 15 years ago in date format
            if birth_date > min_date:
                raise forms.ValidationError("You must be at least 15 years old.")

        return birth_date


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'password1', 'password2')
        field_classes = {"username": UsernameField}

    captcha = ReCaptchaField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("A user is registered with the specified email address!")

        return email


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("There is no user registered with the specified email address!")

        return email
