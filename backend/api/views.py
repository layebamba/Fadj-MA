from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.core.management import call_command
from django.db import models
from .models import MedicineGroup, Supplier, Client, Medicine,Sale,SaleItem
from .serializers import MedicineGroupSerializer, SupplierSerializer, ClientSerializer,MedicineSerializer,SaleSerializer, SaleItemSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Vue pour l'inscription d'un nouvel utilisateur"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Vue pour voir et modifier le profil utilisateur"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    @extend_schema(
            request={
                'multipart/form-data': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'gender': {'type': 'string'},
                        'birth_date': {'type': 'string', 'format': 'date'},
                        'avatar': {'type': 'string', 'format': 'binary'},
                    },
                }
            }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @extend_schema(
            request={
                'multipart/form-data': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'gender': {'type': 'string'},
                        'birth_date': {'type': 'string', 'format': 'date'},
                        'avatar': {'type': 'string', 'format': 'binary'},
                    },
                }
            }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Vue pour changer le mot de passe"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Mot de passe modifié avec succès"
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Vue pour la déconnexion (blacklist du refresh token)"""
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {"message": "Déconnexion réussie"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
class MedicineGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les groupes de médicaments
    Permet: list, create, retrieve, update, delete
    """
    queryset = MedicineGroup.objects.all()
    serializer_class = MedicineGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les fournisseurs
    Permet: list, create, retrieve, update, delete
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les clients
    Permet: list, create, retrieve, update, delete
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    filterset_fields = ['gender']
    ordering_fields = ['last_name', 'created_at']
    ordering = ['last_name', 'first_name']

class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les médicaments
    Permet: list, create, retrieve, update, delete
    """
    queryset = Medicine.objects.select_related('group', 'supplier', 'created_by').all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'medicine_id', 'manufacturer', 'composition']
    filterset_fields = ['group', 'supplier', 'consumption_type', 'pharmaceutical_form']
    ordering_fields = ['name', 'expiration_date', 'stock_quantity', 'selling_price', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Retourne les médicaments avec stock faible"""
        low_stock_medicines = self.queryset.filter(
            stock_quantity__lte=models.F('min_stock_alert')
        )
        serializer = self.get_serializer(low_stock_medicines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Retourne les médicaments expirant dans les 30 jours"""
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        expiring_medicines = self.queryset.filter(
            expiration_date__lte=thirty_days_later,
            expiration_date__gte=timezone.now().date()
        )
        serializer = self.get_serializer(expiring_medicines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Retourne les médicaments expirés"""
        expired_medicines = self.queryset.filter(
            expiration_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(expired_medicines, many=True)
        return Response(serializer.data)

class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les ventes
    Permet: list, create, retrieve (pas de update/delete pour l'intégrité)
    """
    queryset = Sale.objects.select_related('client', 'sold_by').prefetch_related('items__medicine').all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sale_number', 'client__first_name', 'client__last_name']
    filterset_fields = ['payment_method', 'client']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    # Désactiver update et delete pour l'intégrité des ventes
    http_method_names = ['get', 'post', 'head', 'options']

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Retourne les ventes du jour"""
        today_sales = self.queryset.filter(
            created_at__date=timezone.now().date()
        )
        serializer = self.get_serializer(today_sales, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des ventes"""
        from django.db.models import Sum, Count

        today = timezone.now().date()

        stats = {
            'today': {
                'count': self.queryset.filter(created_at__date=today).count(),
                'total': self.queryset.filter(created_at__date=today).aggregate(
                    total=Sum('total_amount')
                )['total'] or 0
            },
            'total': {
                'count': self.queryset.count(),
                'total': self.queryset.aggregate(
                    total=Sum('total_amount')
                )['total'] or 0
            }
        }

        return Response(stats)

class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les lignes de vente (lecture seule)
    Permet: list, retrieve (pas de création/modification)
    """
    queryset = SaleItem.objects.select_related('sale', 'medicine', 'sale__client').all()
    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medicine__name', 'sale__sale_number']
    filterset_fields = ['medicine', 'sale']
    ordering_fields = ['sale__created_at', 'quantity', 'total_price']
    ordering = ['-sale__created_at']

    @action(detail=False, methods=['get'])
    def by_medicine(self, request):
        """Statistiques de vente par médicament"""
        from django.db.models import Sum, Count

        medicine_id = request.query_params.get('medicine_id')
        if not medicine_id:
            return Response(
                {'error': 'medicine_id parameter required'},
                status=400
            )

        stats = self.queryset.filter(medicine_id=medicine_id).aggregate(
            total_quantity=Sum('quantity'),
            total_sales=Count('id'),
            total_revenue=Sum('total_price')
        )

        return Response(stats)



@api_view(['POST'])
@permission_classes([AllowAny])  # À SÉCURISER ou SUPPRIMER après usage
def seed_database(request):
    """Route temporaire pour populer la base en production"""
    try:
        call_command('seed_data')
        return JsonResponse({'message': 'Base de données peuplée avec succès'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
