from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny,IsAuthenticated

from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
)


class SignUpView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=SignUpSerializer)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response({"msg": "me", "data": serializer.data}, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ProfileUpdateSerializer)
    def patch(self, request):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"msg": "Profile updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class PassChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    def put(self, request):
        serializer = PasswordChangeSerializer(
            instance=request.user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        Token.objects.filter(user=request.user).delete()
        new_token, _ = Token.objects.get_or_create(user=request.user)
        return Response({"msg": "Parol ozgartirildi", "token": new_token.key}, status=status.HTTP_200_OK)


class LogOutView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"msg": "Tizimdan chiqdingiz"}, status=status.HTTP_200_OK)