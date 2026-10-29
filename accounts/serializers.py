from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    conf_pass = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "username", "email",
                  "phone_number", "address", "password", "conf_pass"]
        read_only_fields = ["id"]

    def validate(self, data):
        if data.get("password") != data.get("conf_pass"):
            raise ValidationError("Parollar mos emas")
        return data

    def validate_username(self, username):
        if username and username[0].isdigit():
            raise ValidationError("Username raqam bilan boshlanmasin")
        return username

    def create(self, validated_data):
        validated_data.pop("conf_pass")
        return CustomUser.objects.create_user(**validated_data)

    def to_representation(self, instance):
        user = super().to_representation(instance)
        return {"msg": "Royxatdan otdingiz", "user": user}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get("username"), password=data.get("password"))
        if not user:
            raise ValidationError("Parol yoki username xato")
        data["user"] = user
        return data

    def to_representation(self, instance):
        user = instance["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return {"username": user.username, "token": token.key, "role": user.role}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email", "username",
                  "phone_number", "address", "role"]
        read_only_fields = ["id", "role"]


class ProfileUpdateSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        read_only_fields = ["id", "role", "username"]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    conf_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.instance
        if not user.check_password(attrs["old_password"]):
            raise ValidationError("Eski parol xato")
        if attrs["new_password"] == attrs["old_password"]:
            raise ValidationError("Yangi parol eskisiga teng bolmasin")
        if attrs["conf_password"] != attrs["new_password"]:
            raise ValidationError("Yangi parollar mos emas")
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance