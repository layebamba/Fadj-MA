

from django.urls import path,include
from .reports import download_dashboard_report
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    UserDetailView,
    ChangePasswordView,
    logout_view,
    MedicineGroupViewSet,
    SupplierViewSet,
    ClientViewSet,
    MedicineViewSet,
    SaleViewSet,
    SaleItemViewSet,

)

app_name = 'api'
router = DefaultRouter()
router.register(r'medicine-groups', MedicineGroupViewSet, basename='medicine-group')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'sale-items', SaleItemViewSet, basename='sale-item')



urlpatterns = [

    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', UserDetailView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reports/dashboard/', download_dashboard_report, name='dashboard_report'),
    path('', include(router.urls)),
]