from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

Gender = (
    ('male', 'Male'),
    ('female', 'Female')
)

phone_validator = RegexValidator(r"^\d{8}$", "The phone number provided is invalid. It should be 8 digits.")


class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, phone_number, password=None,
                    **extra_fields):
        if not first_name:
            raise ValueError("The First name field must be set")
        if not last_name:
            raise ValueError("The Last name field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")
        if not phone_number:
            raise ValueError("The Phone number field must be set")

        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, username=username, email=email,
                          phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, first_name, username, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(first_name, last_name, username, email, phone_number, password, **extra_fields)

    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=8, validators=[phone_validator], unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=Gender, blank=True, max_length=10)
    photo = models.ImageField(upload_to='images/%y/%m/%d', default='pp.jpeg')
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True)
    is_online = models.BooleanField(default=False)
    last_logout = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super(User, self).save(*args, **kwargs)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phone_number']

    def __str__(self):
        return self.username

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        return True

    @property
    def is_staff(self):
        return self.is_admin
