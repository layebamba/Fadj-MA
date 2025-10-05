from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator,RegexValidator
from decimal import Decimal


class MedicineGroup(models.Model):
    """Groupe/Catégorie de médicaments"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du groupe"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )

    class Meta:
        verbose_name = "Groupe de médicaments"
        verbose_name_plural = "Groupes de médicaments"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Fournisseur de médicaments"""
    phone_regex = RegexValidator(
            regex=r'^\+?221[0-9]{9}$|^[0-9]{9}$',
            message="Format: +221771234567 ou 771234567"
        )

    email_regex = RegexValidator(
            regex=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
            message="Format email invalide (minuscules uniquement)"
        )
    name_regex = RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s\-\']+$',
            message="Uniquement lettres, espaces, tirets et apostrophes"
        )
    name = models.CharField(
        max_length=255,
        validators=[name_regex],
        verbose_name="Nom du fournisseur"
    )
    phone = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        validators=[email_regex],
        verbose_name="Email"
    )
    address = models.TextField(
        verbose_name="Adresse"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']

    def __str__(self):
        return self.name


class Medicine(models.Model):
    """Médicament"""

    CONSUMPTION_TYPES = [
        ('oral', 'Oral'),
        ('injection', 'Injection'),
        ('topique', 'Topique'),
        ('inhalation', 'Inhalation'),
    ]

    PHARMACEUTICAL_FORMS = [
        ('comprime', 'Comprimé'),
        ('gelule', 'Gélule'),
        ('sirop', 'Sirop'),
        ('creme', 'Crème'),
        ('pommade', 'Pommade'),
        ('injection', 'Injection'),
        ('gouttes', 'Gouttes'),
        ('suppositoire', 'Suppositoire'),
        ('autre', 'Autre'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="Nom du médicament"
    )
    medicine_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID médicament"
    )
    group = models.ForeignKey(
        MedicineGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medicines',
        verbose_name="Groupe"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medicines',
        verbose_name="Fournisseur"
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Quantité en stock"
    )
    min_stock_alert = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        verbose_name="Seuil d'alerte stock"
    )
    composition = models.TextField(
        blank=True,
        default='',
        verbose_name="Composition"
    )
    manufacturer = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Fabricant/Commerçant"
    )
    consumption_type = models.CharField(
        max_length=20,
        choices=CONSUMPTION_TYPES,
        blank=True,
        default='oral',
        verbose_name="Type de consommation"
    )
    expiration_date = models.DateField(
    null=True,
    blank=True,
    verbose_name="Date d'expiration"
)
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    dosage_info = models.TextField(
        blank=True,
        verbose_name="Dosage et posologie"
    )
    active_ingredients = models.TextField(
        blank=True,
        verbose_name="Ingrédients actifs"
    )
    side_effects = models.TextField(
        blank=True,
        verbose_name="Effets secondaires"
    )
    pharmaceutical_form = models.CharField(
        max_length=20,
        choices=PHARMACEUTICAL_FORMS,
        blank=True,
        default='comprime',
        verbose_name="Forme pharmaceutique"
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix d'achat (FCFA)"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix de vente (FCFA)"
    )
    image = models.ImageField(
        upload_to='medicines/',
        blank=True,
        null=True,
        verbose_name="Image"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medicines',
        verbose_name="Créé par"
    )

    class Meta:
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"
        ordering = ['name']
        indexes = [
            models.Index(fields=['medicine_id']),
            models.Index(fields=['name']),
            models.Index(fields=['expiration_date']),
        ]

    def save(self, *args, **kwargs):
        if not self.medicine_id:
            import time
            timestamp = str(int(time.time() * 1000))[-9:]
            self.medicine_id = f"D06ID{timestamp}"
        super(Medicine, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.medicine_id})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_alert

    @property
    def profit_margin(self):
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0


class Client(models.Model):
    """Client de la pharmacie"""
    phone_regex = RegexValidator(
            regex=r'^\+?221[0-9]{9}$|^[0-9]{9}$',
            message="Format: +221771234567 ou 771234567"
        )
    email_regex = RegexValidator(
                regex=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
                message="Format email invalide (minuscules uniquement)"
            )
    name_regex = RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s\-\']+$',
            message="Uniquement lettres, espaces, tirets et apostrophes"
        )
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]

    first_name = models.CharField(
        max_length=100,
        validators=[name_regex],
        verbose_name="Prénom"
    )
    last_name = models.CharField(
        max_length=100,
        validators=[name_regex],
        verbose_name="Nom"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Genre"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    phone = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        blank=True,
        validators=[email_regex],
        verbose_name="Email"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Adresse"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Sale(models.Model):
    """Vente de médicaments"""

    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('card', 'Carte bancaire'),
        ('mobile', 'Mobile money'),
        ('check', 'Chèque'),
    ]

    sale_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de vente"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        verbose_name="Client"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant total (FCFA)"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Méthode de paiement"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
        verbose_name="Vendu par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de vente"
    )

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Vente {self.sale_number} - {self.total_amount} FCFA"

    def save(self, *args, **kwargs):
        if not self.sale_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.sale_number = f"VNT-{timestamp}"
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    """Détail d'une vente"""

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Vente"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name='sale_items',
        verbose_name="Médicament"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix unitaire (FCFA)"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix total (FCFA)"
    )

    class Meta:
        verbose_name = "Ligne de vente"
        verbose_name_plural = "Lignes de vente"

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.medicine.stock_quantity -= self.quantity
        self.medicine.save()