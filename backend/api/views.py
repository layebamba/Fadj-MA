from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from users.serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


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
