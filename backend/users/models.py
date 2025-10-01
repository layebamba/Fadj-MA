from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requis')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    username = None

    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]

    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('admin', 'Administrateur'),

        ('pharmacist', 'Pharmacien'),
    ]
    email_regex = RegexValidator(
            regex=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
            message="Format email invalide (minuscules uniquement)"
        )
    phone_regex = RegexValidator(
            regex=r'^\+?221[0-9]{9}$|^[0-9]{9}$',
            message="Format: +221771234567 ou 771234567"
        )
    email = models.EmailField(
             validators=[email_regex],
             unique=True,
             verbose_name="Email"
         )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name="Genre"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_regex],
        verbose_name="Téléphone"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name="Rôle"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Utilisateur')
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']