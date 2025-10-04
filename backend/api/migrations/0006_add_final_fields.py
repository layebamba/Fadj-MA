from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_add_missing_fields'),
    ]

    operations = [

        migrations.AddField(
            model_name='medicine',
            name='active_ingredients',
            field=models.TextField(blank=True, default='', verbose_name='Ingrédients actifs'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='side_effects',
            field=models.TextField(blank=True, default='', verbose_name='Effets secondaires'),
        ),
    ]