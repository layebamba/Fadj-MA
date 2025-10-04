from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_alter_medicine_composition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicine',
            name='composition',
            field=models.TextField(blank=True, default='', verbose_name='Composition'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='manufacturer',
            field=models.CharField(max_length=255, blank=True, default='', verbose_name='Fabricant/Commerçant'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='consumption_type',
            field=models.CharField(max_length=20, blank=True, default='oral', verbose_name='Type de consommation'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='expiration_date',
            field=models.DateField(null=True, blank=True, verbose_name="Date d'expiration"),
        ),
        migrations.AddField(
            model_name='medicine',
            name='pharmaceutical_form',
            field=models.CharField(max_length=20, blank=True, default='comprime', verbose_name='Forme pharmaceutique'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='purchase_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name="Prix d'achat (FCFA)"),
        ),
        migrations.AddField(
            model_name='medicine',
            name='group',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='api.medicinegroup', related_name='medicines', verbose_name='Groupe'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='supplier',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='api.supplier', related_name='medicines', verbose_name='Fournisseur'),
        ),
    ]