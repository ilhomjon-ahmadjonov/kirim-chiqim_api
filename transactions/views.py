from decimal import Decimal
from datetime import date as date_cls
from django.db.models import Sum
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .rates import update_rates_from_cbu
from . import services
from .models import Account, Currency, Expense, ExpenseType, Income, IncomeType, Transfer
from .serializers import (
    AccountSerializer, ExpenseSerializer, ExpenseTypeSerializer,
    IncomeSerializer, IncomeTypeSerializer, TransferSerializer,
)
from .services import convert


class OwnerScopedMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()

        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()

        qs = self.queryset.all()
        if user.is_admin_role:
            return qs
        return qs.filter(owner=user)


class AccountViewSet(OwnerScopedMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class IncomeTypeViewSet(viewsets.ModelViewSet):
    queryset = IncomeType.objects.all()
    serializer_class = IncomeTypeSerializer
    permission_classes = [IsAuthenticated]


class ExpenseTypeViewSet(viewsets.ModelViewSet):
    queryset = ExpenseType.objects.all()
    serializer_class = ExpenseTypeSerializer
    permission_classes = [IsAuthenticated]


class IncomeViewSet(OwnerScopedMixin,
                    mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Income.objects.select_related("account", "income_type")
    serializer_class = IncomeSerializer
    filterset_fields = ["account", "income_type", "currency", "date"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = services.create_income(owner=request.user, **serializer.validated_data)
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class ExpenseViewSet(OwnerScopedMixin,
                     mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Expense.objects.select_related("account", "expense_type")
    serializer_class = ExpenseSerializer
    filterset_fields = ["account", "expense_type", "currency", "date"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = services.create_expense(owner=request.user, **serializer.validated_data)
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class TransferViewSet(OwnerScopedMixin,
                      mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Transfer.objects.select_related("source", "target")
    serializer_class = TransferSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = services.create_transfer(owner=request.user, **serializer.validated_data)
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = request.query_params.get("kind", "expense")
        display = request.query_params.get("currency", Currency.UZS)
        month_str = request.query_params.get("month", date_cls.today().strftime("%Y-%m"))
        year, month = map(int, month_str.split("-"))

        if kind == "income":
            model, field = Income, "income_type__name"
        else:
            model, field = Expense, "expense_type__name"

        qs = model.objects.filter(date__year=year, date__month=month)
        if not request.user.is_admin_role:
            qs = qs.filter(owner=request.user)

        rows = list(qs.values(field).annotate(total_uzs=Sum("amount_uzs")).order_by("-total_uzs"))
        grand_uzs = sum((r["total_uzs"] for r in rows), Decimal("0"))

        items = []
        for r in rows:
            share = (r["total_uzs"] / grand_uzs * 100).quantize(Decimal("0.1")) if grand_uzs else Decimal("0")
            items.append({
                "name": r[field],
                "amount": convert(r["total_uzs"], Currency.UZS, display),
                "percent": share,
            })

        return Response({
            "month": month_str,
            "kind": kind,
            "currency": display,
            "total": convert(grand_uzs, Currency.UZS, display),
            "items": items,
        })


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        display = request.query_params.get("currency", Currency.UZS)
        accounts = Account.objects.filter(owner=request.user)
        total = sum((convert(a.balance, a.currency, display) for a in accounts), Decimal("0"))
        return Response({"currency": display, "total": total})




class UpdateRatesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_admin_role:
            return Response({"detail": "Faqat admin"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"msg": "Kurslar yangilandi", "rates": update_rates_from_cbu()})