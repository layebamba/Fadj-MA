from rest_framework import serializers
from .models import MedicineGroup, Supplier, Client, Medicine,Sale,SaleItem

class MedicineGroupSerializer(serializers.ModelSerializer):
    """Serializer pour les groupes de médicaments"""

    medicines_count = serializers.SerializerMethodField()

    class Meta:
        model = MedicineGroup
        fields = [
            'id',
            'name',
            'description',
            'medicines_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_medicines_count(self, obj):
        """Retourne le nombre de médicaments dans ce groupe"""
        return obj.medicines.count()

class SupplierSerializer(serializers.ModelSerializer):
    """Serializer pour les fournisseurs"""

    medicines_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'address',
            'medicines_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_medicines_count(self, obj):
        """Retourne le nombre de médicaments fournis"""
        return obj.medicines.count()

class ClientSerializer(serializers.ModelSerializer):
    """Serializer pour les clients"""

    full_name = serializers.ReadOnlyField()
    purchases_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'birth_date',
            'phone',
            'email',
            'address',
            'purchases_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']

    def get_purchases_count(self, obj):
        """Retourne le nombre d'achats du client"""
        return obj.sales.count()

class MedicineSerializer(serializers.ModelSerializer):
    """Serializer pour les médicaments"""

    # Relations - affichage détaillé en lecture
    group_detail = MedicineGroupSerializer(source='group', read_only=True)
    supplier_detail = SupplierSerializer(source='supplier', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    # Propriétés calculées
    is_low_stock = serializers.ReadOnlyField()
    profit_margin = serializers.ReadOnlyField()

    # Image
    image = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = Medicine
        fields = [
            'id',
            'name',
            'medicine_id',
            'group',
            'group_detail',
            'supplier',
            'supplier_detail',
            'stock_quantity',
            'min_stock_alert',
            'is_low_stock',
            'composition',
            'manufacturer',
            'consumption_type',
            'expiration_date',
            'description',
            'dosage_info',
            'active_ingredients',
            'side_effects',
            'pharmaceutical_form',
            'purchase_price',
            'selling_price',
            'profit_margin',
            'image',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'is_low_stock',
            'profit_margin',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]

    def create(self, validated_data):
        """Ajouter l'utilisateur connecté comme créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer pour les lignes de vente"""

    medicine_name = serializers.CharField(source='medicine.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id',
            'medicine',
            'medicine_name',
            'quantity',
            'unit_price',
            'total_price'
        ]
        read_only_fields = ['id', 'total_price']

    def validate(self, data):
        """Vérifier que le stock est suffisant"""
        medicine = data.get('medicine')
        quantity = data.get('quantity')

        if medicine and quantity:
            if medicine.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Stock insuffisant. Disponible: {medicine.stock_quantity}'
                })

        return data


class SaleSerializer(serializers.ModelSerializer):
    """Serializer pour les ventes"""

    items = SaleItemSerializer(many=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    sold_by_name = serializers.CharField(source='sold_by.full_name', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'sale_number',
            'client',
            'client_name',
            'total_amount',
            'payment_method',
            'notes',
            'sold_by',
            'sold_by_name',
            'items',
            'created_at'
        ]
        read_only_fields = ['id', 'sale_number', 'total_amount', 'sold_by', 'created_at']

    def create(self, validated_data):
        """Créer une vente avec ses lignes"""
        items_data = validated_data.pop('items')

        # Ajouter l'utilisateur connecté comme vendeur
        validated_data['sold_by'] = self.context['request'].user

        # Calculer le montant total
        total = sum(
            item['quantity'] * item['unit_price']
            for item in items_data
        )
        validated_data['total_amount'] = total

        # Créer la vente
        sale = Sale.objects.create(**validated_data)

        # Créer les lignes de vente et mettre à jour le stock
        for item_data in items_data:
            medicine = item_data['medicine']
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']

            # Créer la ligne
            SaleItem.objects.create(
                sale=sale,
                medicine=medicine,
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price
            )

            medicine.stock_quantity -= quantity
            medicine.save()

        return sale