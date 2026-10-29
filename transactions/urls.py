from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, IncomeTypeViewSet, ExpenseTypeViewSet,
    IncomeViewSet, ExpenseViewSet, TransferViewSet,
    StatisticsView, SummaryView,UpdateRatesView
)

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="account")
router.register("income-types", IncomeTypeViewSet, basename="income-type")
router.register("expense-types", ExpenseTypeViewSet, basename="expense-type")
router.register("incomes", IncomeViewSet, basename="income")
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("transfers", TransferViewSet, basename="transfer")

urlpatterns = [
    path("", include(router.urls)),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("summary/", SummaryView.as_view(), name="summary"),
    path("rates/update/", UpdateRatesView.as_view(), name="rates-update"),
]