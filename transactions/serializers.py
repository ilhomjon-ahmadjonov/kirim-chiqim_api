from rest_framework import serializers
from .models import Account, Expense, ExpenseType, Income, IncomeType, Transfer


def check_owner(user, account):
    if account.owner_id != user.id:
        raise serializers.ValidationError("Bu hisob sizga tegishli emas")
    return account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "kind", "currency", "balance"]
        read_only_fields = ["id", "balance"]


class IncomeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeType
        fields = ["id", "name"]


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = ["id", "name"]


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ["id", "account", "income_type", "amount", "currency",
                  "amount_in_account", "amount_uzs", "date", "description"]
        read_only_fields = ["id", "amount_in_account", "amount_uzs"]

    def validate_account(self, account):
        return check_owner(self.context["request"].user, account)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "account", "expense_type", "amount", "currency",
                  "amount_in_account", "amount_uzs", "date", "description"]
        read_only_fields = ["id", "amount_in_account", "amount_uzs"]

    def validate_account(self, account):
        return check_owner(self.context["request"].user, account)


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ["id", "source", "target", "amount", "received_amount", "created_at"]
        read_only_fields = ["id", "received_amount", "created_at"]

    def validate_source(self, account):
        return check_owner(self.context["request"].user, account)

    def validate_target(self, account):
        return check_owner(self.context["request"].user, account)

    def validate(self, data):
        if data["source"] == data["target"]:
            raise serializers.ValidationError("Bir xil hisobga o'tkazib bo'lmaydi")
        return data