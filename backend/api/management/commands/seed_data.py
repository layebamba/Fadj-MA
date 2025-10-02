from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from api.models import MedicineGroup, Supplier, Medicine
from decimal import Decimal
from datetime import date
import requests

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée uniquement les médicaments avec images placeholder'

    def download_placeholder_image(self, seed=None):
        """Télécharge une image placeholder"""
        try:
            url = f"https://picsum.photos/400/400"
            if seed:
                url += f"?random={seed}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content, name=f'medicine_{seed}.jpg')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erreur téléchargement image: {e}'))
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Création des médicaments avec images...'))

        # Récupérer un utilisateur existant ou le premier admin
        try:
            user = User.objects.filter(role='pharmacist').first() or User.objects.filter(is_staff=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('Aucun utilisateur pharmacien ou admin trouvé. Créez-en un d\'abord.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur: {e}'))
            return

        # Récupérer les groupes existants
        groups = list(MedicineGroup.objects.all().order_by('id'))
        if len(groups) < 6:
            self.stdout.write(self.style.ERROR(f'Seulement {len(groups)} groupes trouvés. Créez au moins 6 groupes d\'abord.'))
            return

        # Récupérer les fournisseurs existants
        suppliers = list(Supplier.objects.all().order_by('id'))
        if len(suppliers) < 5:
            self.stdout.write(self.style.ERROR(f'Seulement {len(suppliers)} fournisseurs trouvés. Créez au moins 5 fournisseurs d\'abord.'))
            return

        # Données des médicaments
        medicines_data = [
            {
                'name': 'Paracétamol 500mg', 'medicine_id': 'MED-2024-001',
                'group': groups[1], 'supplier': suppliers[0],
                'stock_quantity': 250, 'min_stock_alert': 50,
                'composition': 'Paracétamol', 'manufacturer': 'Sanofi Sénégal',
                'consumption_type': 'oral', 'expiration_date': date(2026, 6, 30),
                'description': 'Le Paracétamol est un médicament antalgique et antipyrétique efficace pour soulager les douleurs légères à modérées et réduire la fièvre. Il agit en inhibant la synthèse des prostaglandines au niveau du système nerveux central. Ce médicament est particulièrement indiqué pour traiter les maux de tête, les douleurs dentaires, les courbatures, les règles douloureuses et les états grippaux. Il est généralement bien toléré aux doses recommandées et peut être utilisé chez les adultes, les enfants et les femmes enceintes sous surveillance médicale.',
                'dosage_info': '1 à 2 comprimés toutes les 4-6 heures, maximum 8 par jour',
                'active_ingredients': 'Paracétamol 500mg',
                'side_effects': 'Rares : réactions allergiques, atteintes hépatiques à forte dose',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('500'), 'selling_price': Decimal('750'),
            },
            {
                'name': 'Coartem 20/120mg', 'medicine_id': 'MED-2024-002',
                'group': groups[2], 'supplier': suppliers[1],
                'stock_quantity': 150, 'min_stock_alert': 30,
                'composition': 'Artéméther + Luméfantrine', 'manufacturer': 'Novartis',
                'consumption_type': 'oral', 'expiration_date': date(2026, 9, 15),
                'description': 'Coartem est une association thérapeutique à base d\'artéméther et de luméfantrine, deux antipaludiques qui agissent en synergie contre le Plasmodium falciparum, parasite responsable du paludisme. Ce traitement de première intention recommandé par l\'OMS est efficace contre les formes simples de paludisme non compliquées. Il agit rapidement en détruisant les parasites présents dans les globules rouges. Le traitement doit être pris avec un repas gras pour améliorer son absorption. Il est essentiel de respecter la durée complète du traitement même si les symptômes disparaissent rapidement.',
                'dosage_info': '4 comprimés 2 fois par jour pendant 3 jours',
                'active_ingredients': 'Artéméther 20mg, Luméfantrine 120mg',
                'side_effects': 'Maux de tête, vertiges, nausées, douleurs musculaires',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('3500'), 'selling_price': Decimal('5000'),
            },
            {
                'name': 'Amoxicilline 1g', 'medicine_id': 'MED-2024-003',
                'group': groups[0], 'supplier': suppliers[0],
                'stock_quantity': 200, 'min_stock_alert': 40,
                'composition': 'Amoxicilline trihydrate', 'manufacturer': 'Laboratoires Afrique Pharma',
                'consumption_type': 'oral', 'expiration_date': date(2026, 12, 31),
                'description': 'L\'Amoxicilline est un antibiotique de la famille des bêta-lactamines à large spectre d\'action. Elle est efficace contre de nombreuses bactéries responsables d\'infections courantes telles que les otites, les sinusites, les infections urinaires, les infections respiratoires et certaines infections cutanées. Ce médicament agit en empêchant la synthèse de la paroi bactérienne, ce qui entraîne la destruction des bactéries. Il est important de respecter la durée du traitement prescrite même si les symptômes s\'améliorent rapidement, afin d\'éviter les résistances bactériennes et les rechutes.',
                'dosage_info': '1g 2 à 3 fois par jour pendant 7 à 10 jours',
                'active_ingredients': 'Amoxicilline 1g',
                'side_effects': 'Diarrhée, nausées, éruptions cutanées, candidoses',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('2000'), 'selling_price': Decimal('3000'),
            },
            {
                'name': 'Metformine 850mg', 'medicine_id': 'MED-2024-004',
                'group': groups[3], 'supplier': suppliers[2],
                'stock_quantity': 180, 'min_stock_alert': 35,
                'composition': 'Chlorhydrate de metformine', 'manufacturer': 'Sanofi',
                'consumption_type': 'oral', 'expiration_date': date(2027, 3, 20),
                'description': 'La Metformine est le traitement de première intention du diabète de type 2. Elle agit en diminuant la production de glucose par le foie, en améliorant la sensibilité des cellules à l\'insuline et en ralentissant l\'absorption des glucides au niveau intestinal. Ce médicament aide à contrôler la glycémie sans provoquer d\'hypoglycémie. Il présente également des effets bénéfiques sur le poids et les paramètres cardiovasculaires. La Metformine doit être prise pendant les repas pour minimiser les effets digestifs. Elle est souvent associée à des mesures hygiéno-diététiques comprenant une alimentation équilibrée et une activité physique régulière.',
                'dosage_info': '1 comprimé 2 à 3 fois par jour pendant les repas',
                'active_ingredients': 'Metformine 850mg',
                'side_effects': 'Troubles digestifs, diarrhée, nausées, goût métallique',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('1500'), 'selling_price': Decimal('2200'),
            },
            {
                'name': 'Vitamine C 1000mg', 'medicine_id': 'MED-2024-005',
                'group': groups[4], 'supplier': suppliers[3],
                'stock_quantity': 300, 'min_stock_alert': 60,
                'composition': 'Acide ascorbique', 'manufacturer': 'Bayer',
                'consumption_type': 'oral', 'expiration_date': date(2026, 11, 30),
                'description': 'La Vitamine C ou acide ascorbique est un complément alimentaire essentiel pour le bon fonctionnement de l\'organisme. Elle joue un rôle crucial dans le renforcement du système immunitaire, la protection des cellules contre le stress oxydatif, la synthèse du collagène pour la santé de la peau et des articulations, et l\'absorption du fer. Elle est particulièrement recommandée en période de fatigue, lors des changements de saison, pendant la convalescence ou en cas de carences alimentaires. Cette forme effervescente assure une dissolution rapide et une absorption optimale. La vitamine C contribue à réduire la fatigue et participe au métabolisme énergétique normal.',
                'dosage_info': '1 comprimé effervescent par jour',
                'active_ingredients': 'Acide ascorbique 1000mg',
                'side_effects': 'Troubles digestifs à forte dose',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('800'), 'selling_price': Decimal('1200'),
            },
            {
                'name': 'Amlodipine 5mg', 'medicine_id': 'MED-2024-006',
                'group': groups[5], 'supplier': suppliers[1],
                'stock_quantity': 120, 'min_stock_alert': 25,
                'composition': "Bésilate d'amlodipine", 'manufacturer': 'Pfizer',
                'consumption_type': 'oral', 'expiration_date': date(2027, 1, 15),
                'description': 'L\'Amlodipine est un antihypertenseur de la famille des inhibiteurs calciques. Elle agit en relaxant et en dilatant les vaisseaux sanguins, ce qui facilite la circulation du sang et réduit la pression artérielle. Elle est utilisée dans le traitement de l\'hypertension artérielle et de certaines formes d\'angine de poitrine. Ce médicament permet de réduire les risques cardiovasculaires associés à l\'hypertension tels que les accidents vasculaires cérébraux et les infarctus du myocarde. Son effet antihypertenseur est progressif et durable, nécessitant une prise quotidienne régulière. Le traitement doit être associé à des mesures hygiéno-diététiques incluant la réduction de la consommation de sel et une activité physique régulière.',
                'dosage_info': '1 comprimé par jour, de préférence le matin',
                'active_ingredients': 'Amlodipine 5mg',
                'side_effects': 'Œdèmes des chevilles, bouffées de chaleur, fatigue',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('2500'), 'selling_price': Decimal('3500'),
            },
            {
                'name': 'Augmentin 1g', 'medicine_id': 'MED-2024-007',
                'group': groups[0], 'supplier': suppliers[4],
                'stock_quantity': 90, 'min_stock_alert': 20,
                'composition': 'Amoxicilline + Acide clavulanique', 'manufacturer': 'GSK',
                'consumption_type': 'oral', 'expiration_date': date(2026, 8, 20),
                'description': 'Augmentin est une association d\'amoxicilline et d\'acide clavulanique qui renforce l\'efficacité antibiotique. L\'acide clavulanique est un inhibiteur de bêta-lactamases, des enzymes produites par certaines bactéries pour résister aux antibiotiques. Cette combinaison permet de traiter des infections causées par des bactéries résistantes à l\'amoxicilline seule. Augmentin est indiqué dans le traitement des infections ORL, respiratoires, urinaires, dentaires et cutanées. Il est particulièrement efficace contre les bactéries productrices de bêta-lactamases. Ce médicament doit être pris en début de repas pour optimiser son absorption et réduire les troubles digestifs. Il est essentiel de respecter la durée complète du traitement prescrit.',
                'dosage_info': '1 comprimé 2 à 3 fois par jour pendant 7 jours',
                'active_ingredients': 'Amoxicilline 875mg, Acide clavulanique 125mg',
                'side_effects': 'Diarrhée, nausées, candidoses, éruptions cutanées',
                'pharmaceutical_form': 'comprime',
                'purchase_price': Decimal('4000'), 'selling_price': Decimal('5500'),
            },
            {
                'name': 'Bronchodex Sirop', 'medicine_id': 'MED-2024-008',
                'group': groups[1], 'supplier': suppliers[0],
                'stock_quantity': 75, 'min_stock_alert': 15,
                'composition': 'Dextrométhorphane + Guaifénésine', 'manufacturer': 'Laboratoires Afrique Pharma',
                'consumption_type': 'oral', 'expiration_date': date(2026, 5, 30),
                'description': 'Bronchodex est un sirop antitussif et expectorant qui associe deux principes actifs complémentaires. Le dextrométhorphane est un antitussif qui calme la toux sèche en agissant sur le centre de la toux au niveau du cerveau, tandis que la guaifénésine est un expectorant qui fluidifie les sécrétions bronchiques et facilite leur évacuation. Ce médicament est particulièrement indiqué lors des infections respiratoires accompagnées de toux irritative ou productive. Il aide à améliorer le confort respiratoire et favorise un sommeil réparateur. Le sirop doit être pris à l\'aide de la cuillère-mesure fournie. Il est recommandé de boire suffisamment d\'eau pendant le traitement pour faciliter l\'élimination des sécrétions.',
                'dosage_info': '10ml 3 fois par jour',
                'active_ingredients': 'Dextrométhorphane 15mg/5ml, Guaifénésine 100mg/5ml',
                'side_effects': 'Somnolence, nausées, vertiges',
                'pharmaceutical_form': 'sirop',
                'purchase_price': Decimal('3000'), 'selling_price': Decimal('4200'),
            },
        ]

        created_count = 0
        for idx, data in enumerate(medicines_data, 1):
            medicine, created = Medicine.objects.get_or_create(
                medicine_id=data['medicine_id'],
                defaults={**data, 'created_by': user}
            )

            if created:
                # Télécharger et ajouter une image
                self.stdout.write(f'Téléchargement image pour {medicine.name}...')
                image_file = self.download_placeholder_image(seed=idx)

                if image_file:
                    medicine.image = image_file
                    medicine.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {medicine.name} (avec image)'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ✓ {medicine.name} (sans image - erreur téléchargement)'))

                created_count += 1
            else:
                self.stdout.write(f'  - {medicine.name} (déjà existant)')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Terminé! {created_count} médicaments créés avec images.'))
        if created_count == 0:
            self.stdout.write(self.style.WARNING('Tous les médicaments existaient déjà dans la base.'))