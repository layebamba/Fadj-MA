from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator



User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les informations utilisateur"""
    avatar = serializers.ImageField(required=False, allow_null=True, use_url=True)


    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'gender', 'birth_date', 'phone',
            'role', 'avatar', 'full_name', 'role_display'
        ]
        read_only_fields = ['id', 'full_name', 'role_display']
        extra_kwargs = {
                    'avatar': {'required': False, 'allow_null': True}
                }
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription"""

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = User
        fields = [
             'email', 'password', 'password2',
            'first_name', 'last_name', 'gender', 'birth_date',
            'phone', 'role'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Vérifier que les mots de passe correspondent"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Les mots de passe ne correspondent pas."
            })
        return attrs

    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop('password2')

        user = User.objects.create_user(

            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', ''),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),

            role=validated_data.get('role', 'user'),
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Les mots de passe ne correspondent pas."
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
