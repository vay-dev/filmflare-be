from django.shortcuts import render
from rest_framework import generics, status, permissions
from .serializers import RegisterSerializer, UserUpdateSerializer, ChangePasswordSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response


# Create your views here.


class RegisterUserAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['roles'] = 'admin' if (user.is_staff or user.is_superuser) else user.roles
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get('request')

        # method for including user data in the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'roles': 'admin' if (self.user.is_staff or self.user.is_superuser) else self.user.roles,
            'profile_image': request.build_absolute_uri(self.user.profile_image.url) if self.user.profile_image else None,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'password updated successfully'}, status=status.HTTP_200_OK)
