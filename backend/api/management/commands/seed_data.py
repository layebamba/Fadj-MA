from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from api.models import MedicineGroup, Supplier, Client, Medicine
from decimal import Decimal
from datetime import date
import requests

User = get_user_model()


class Command(BaseCommand):
    help = 'Peuple la base avec groupes, suppliers, clients et médicaments'

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
        self.stdout.write(self.style.SUCCESS('Peuplement de la base de données...'))

        # Récupérer ou créer un utilisateur
        user = User.objects.filter(role='pharmacist').first() or User.objects.filter(is_staff=True).first()
        if not user:
            self.stdout.write(self.style.WARNING('Aucun utilisateur trouvé, création d\'un pharmacien par défaut...'))
            user = User.objects.create_user(
                email='pharmacien@fadjma.sn',
                first_name='Modou',
                last_name='Fall',
                role='pharmacist',
                password='Passer123!'
            )
            self.stdout.write(self.style.SUCCESS(f'Utilisateur créé: {user.email}'))

        # 1. GROUPES
        self.stdout.write('\n1. Création des groupes...')
        groups_data = [
            {'name': 'Antibiotiques', 'description': 'Médicaments pour traiter les infections bactériennes'},
            {'name': 'Antalgiques', 'description': 'Médicaments contre la douleur'},
            {'name': 'Antipaludéens', 'description': 'Médicaments pour le traitement du paludisme'},
            {'name': 'Antidiabétiques', 'description': 'Médicaments pour le contrôle du diabète'},
            {'name': 'Vitamines et Compléments', 'description': 'Suppléments vitaminiques'},
            {'name': 'Médicaments cardiovasculaires', 'description': 'Médicaments pour le cœur'},
        ]
        groups = []
        for data in groups_data:
            group, created = MedicineGroup.objects.get_or_create(**data)
            groups.append(group)
            status = 'créé' if created else 'existant'
            self.stdout.write(f'  ✓ {group.name} ({status})')

        # 2. SUPPLIERS
        self.stdout.write('\n2. Création des fournisseurs...')
        suppliers_data = [
            {'name': 'Laboratoires Afrique Pharma', 'phone': '338234567', 'email': 'contact@afriquepharma.sn', 'address': 'Zone industrielle, Rufisque'},
            {'name': 'Sodipharm Sénégal', 'phone': '771456789', 'email': 'info@sodipharm.sn', 'address': 'Route de Ouakam, Dakar'},
            {'name': 'Distrimed International', 'phone': '775123456', 'email': 'ventes@distrimed.sn', 'address': 'Boulevard du Centenaire, Dakar'},
            {'name': 'Copharmed Distribution', 'phone': '338567890', 'email': 'commandes@copharmed.sn', 'address': 'Liberté 6, Dakar'},
            {'name': "Pharm'Access Sénégal", 'phone': '772345678', 'email': 'contact@pharmaccess.sn', 'address': 'Point E, Dakar'},
        ]
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(name=data['name'], defaults=data)
            suppliers.append(supplier)
            status = 'créé' if created else 'existant'
            self.stdout.write(f'  ✓ {supplier.name} ({status})')

        # 3. CLIENTS
        self.stdout.write('\n3. Création des clients...')
        clients_data = [
            {'first_name': 'Moussa', 'last_name': 'Ndiaye', 'gender': 'M', 'birth_date': date(1985, 3, 20), 'phone': '776543210', 'email': 'moussa.ndiaye@email.sn', 'address': 'Plateau, Dakar'},
            {'first_name': 'Fatou', 'last_name': 'Sall', 'gender': 'F', 'birth_date': date(1992, 7, 10), 'phone': '775432109', 'email': 'fatou.sall@gmail.com', 'address': 'Ouakam, Dakar'},
            {'first_name': 'Ibrahima', 'last_name': 'Diop', 'gender': 'M', 'birth_date': date(1978, 11, 30), 'phone': '773210987', 'email': 'idiop@yahoo.fr', 'address': 'Grand Yoff, Dakar'},
            {'first_name': 'Awa', 'last_name': 'Ba', 'gender': 'F', 'birth_date': date(1995, 1, 25), 'phone': '778765432', 'email': 'awa.ba@outlook.com', 'address': 'Sacré Coeur, Dakar'},
            {'first_name': 'Cheikh', 'last_name': 'Sy', 'gender': 'M', 'birth_date': date(1988, 9, 15), 'phone': '774567890', 'email': 'cheikh.sy@hotmail.com', 'address': 'Mermoz, Dakar'},
            {'first_name': 'Mariama', 'last_name': 'Kane', 'gender': 'F', 'birth_date': date(1980, 12, 5), 'phone': '779876543', 'email': 'mariama.kane@gmail.com', 'address': 'HLM, Dakar'},
        ]
        for data in clients_data:
            client, created = Client.objects.get_or_create(phone=data['phone'], defaults=data)
            status = 'créé' if created else 'existant'
            self.stdout.write(f'  ✓ {client.full_name} ({status})')

        # 4. MÉDICAMENTS
        self.stdout.write('\n4. Création des médicaments avec images...')
        medicines_data = [
            {
                'name': 'Paracétamol 500mg', 'medicine_id': 'MED-2024-001', 'group': groups[1], 'supplier': suppliers[0],
                'stock_quantity': 250, 'min_stock_alert': 50, 'composition': 'Paracétamol', 'manufacturer': 'Sanofi Sénégal',
                'consumption_type': 'oral', 'expiration_date': date(2026, 6, 30),
                'description': 'Le Paracétamol est un médicament antalgique et antipyrétique efficace pour soulager les douleurs légères à modérées et réduire la fièvre. Il agit en inhibant la synthèse des prostaglandines au niveau du système nerveux central. Ce médicament est particulièrement indiqué pour traiter les maux de tête, les douleurs dentaires, les courbatures, les règles douloureuses et les états grippaux.',
                'dosage_info': '1 à 2 comprimés toutes les 4-6 heures, maximum 8 par jour',
                'active_ingredients': 'Paracétamol 500mg',
                'side_effects': 'Rares : réactions allergiques, atteintes hépatiques à forte dose',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('500'), 'selling_price': Decimal('750'),
            },
            {
                'name': 'Coartem 20/120mg', 'medicine_id': 'MED-2024-002', 'group': groups[2], 'supplier': suppliers[1],
                'stock_quantity': 150, 'min_stock_alert': 30, 'composition': 'Artéméther + Luméfantrine', 'manufacturer': 'Novartis',
                'consumption_type': 'oral', 'expiration_date': date(2026, 9, 15),
                'description': 'Coartem est une association thérapeutique recommandée par l\'OMS, efficace contre les formes simples de paludisme. Il agit rapidement en détruisant les parasites présents dans les globules rouges. Le traitement doit être pris avec un repas gras pour améliorer son absorption.',
                'dosage_info': '4 comprimés 2 fois par jour pendant 3 jours',
                'active_ingredients': 'Artéméther 20mg, Luméfantrine 120mg',
                'side_effects': 'Maux de tête, vertiges, nausées, douleurs musculaires',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('3500'), 'selling_price': Decimal('5000'),
            },
            {
                'name': 'Amoxicilline 1g', 'medicine_id': 'MED-2024-003', 'group': groups[0], 'supplier': suppliers[0],
                'stock_quantity': 200, 'min_stock_alert': 40, 'composition': 'Amoxicilline trihydrate', 'manufacturer': 'Laboratoires Afrique Pharma',
                'consumption_type': 'oral', 'expiration_date': date(2026, 12, 31),
                'description': 'Antibiotique à large spectre efficace contre les infections ORL, respiratoires, urinaires et cutanées. Il agit en empêchant la synthèse de la paroi bactérienne.',
                'dosage_info': '1g 2 à 3 fois par jour pendant 7 à 10 jours',
                'active_ingredients': 'Amoxicilline 1g',
                'side_effects': 'Diarrhée, nausées, éruptions cutanées',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('2000'), 'selling_price': Decimal('3000'),
            },
            {
                'name': 'Metformine 850mg', 'medicine_id': 'MED-2024-004', 'group': groups[3], 'supplier': suppliers[2],
                'stock_quantity': 180, 'min_stock_alert': 35, 'composition': 'Chlorhydrate de metformine', 'manufacturer': 'Sanofi',
                'consumption_type': 'oral', 'expiration_date': date(2027, 3, 20),
                'description': 'Traitement de première intention du diabète de type 2. Aide à contrôler la glycémie sans provoquer d\'hypoglycémie.',
                'dosage_info': '1 comprimé 2 à 3 fois par jour pendant les repas',
                'active_ingredients': 'Metformine 850mg',
                'side_effects': 'Troubles digestifs, diarrhée, nausées',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('1500'), 'selling_price': Decimal('2200'),
            },
            {
                'name': 'Vitamine C 1000mg', 'medicine_id': 'MED-2024-005', 'group': groups[4], 'supplier': suppliers[3],
                'stock_quantity': 300, 'min_stock_alert': 60, 'composition': 'Acide ascorbique', 'manufacturer': 'Bayer',
                'consumption_type': 'oral', 'expiration_date': date(2026, 11, 30),
                'description': 'Complément essentiel pour le système immunitaire et la protection contre le stress oxydatif. Recommandé en période de fatigue.',
                'dosage_info': '1 comprimé effervescent par jour',
                'active_ingredients': 'Acide ascorbique 1000mg',
                'side_effects': 'Troubles digestifs à forte dose',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('800'), 'selling_price': Decimal('1200'),
            },
            {
                'name': 'Amlodipine 5mg', 'medicine_id': 'MED-2024-006', 'group': groups[5], 'supplier': suppliers[1],
                'stock_quantity': 120, 'min_stock_alert': 25, 'composition': "Bésilate d'amlodipine", 'manufacturer': 'Pfizer',
                'consumption_type': 'oral', 'expiration_date': date(2027, 1, 15),
                'description': 'Antihypertenseur qui réduit les risques cardiovasculaires. Nécessite une prise quotidienne régulière.',
                'dosage_info': '1 comprimé par jour, de préférence le matin',
                'active_ingredients': 'Amlodipine 5mg',
                'side_effects': 'Œdèmes des chevilles, bouffées de chaleur',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('2500'), 'selling_price': Decimal('3500'),
            },
            {
                'name': 'Augmentin 1g', 'medicine_id': 'MED-2024-007', 'group': groups[0], 'supplier': suppliers[4],
                'stock_quantity': 90, 'min_stock_alert': 20, 'composition': 'Amoxicilline + Acide clavulanique', 'manufacturer': 'GSK',
                'consumption_type': 'oral', 'expiration_date': date(2026, 8, 20),
                'description': 'Antibiotique renforcé efficace contre les bactéries résistantes. Pour infections ORL, respiratoires et urinaires.',
                'dosage_info': '1 comprimé 2 à 3 fois par jour pendant 7 jours',
                'active_ingredients': 'Amoxicilline 875mg, Acide clavulanique 125mg',
                'side_effects': 'Diarrhée, nausées, éruptions cutanées',
                'pharmaceutical_form': 'comprime', 'purchase_price': Decimal('4000'), 'selling_price': Decimal('5500'),
            },
            {
                'name': 'Bronchodex Sirop', 'medicine_id': 'MED-2024-008', 'group': groups[1], 'supplier': suppliers[0],
                'stock_quantity': 75, 'min_stock_alert': 15, 'composition': 'Dextrométhorphane + Guaifénésine', 'manufacturer': 'Laboratoires Afrique Pharma',
                'consumption_type': 'oral', 'expiration_date': date(2026, 5, 30),
                'description': 'Sirop antitussif et expectorant pour infections respiratoires avec toux.',
                'dosage_info': '10ml 3 fois par jour',
                'active_ingredients': 'Dextrométhorphane 15mg/5ml, Guaifénésine 100mg/5ml',
                'side_effects': 'Somnolence, nausées, vertiges',
                'pharmaceutical_form': 'sirop', 'purchase_price': Decimal('3000'), 'selling_price': Decimal('4200'),
            },
        ]

        created_count = 0
        for idx, data in enumerate(medicines_data, 1):
            medicine, created = Medicine.objects.get_or_create(
                medicine_id=data['medicine_id'],
                defaults={**data, 'created_by': user}
            )

            if created:
                self.stdout.write(f'Téléchargement image pour {medicine.name}...')
                image_file = self.download_placeholder_image(seed=idx)

                if image_file:
                    medicine.image = image_file
                    medicine.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {medicine.name} (avec image)'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ✓ {medicine.name} (sans image)'))

                created_count += 1
            else:
                self.stdout.write(f'  - {medicine.name} (existant)')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Peuplement terminé!'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(groups)} groupes'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(suppliers)} fournisseurs'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(clients_data)} clients'))
        self.stdout.write(self.style.SUCCESS(f'   - {created_count} nouveaux médicaments'))