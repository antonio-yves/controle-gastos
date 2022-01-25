from django.urls import path, include
from rest_framework.routers import DefaultRouter
from controle_gastos.views import ReceitasViewSet, DespesasViewSet, ReceitasPorMes, DespesasPorMes, ResumoMes

route = DefaultRouter()
route.register('receitas', ReceitasViewSet, basename='receitas')
route.register('despesas', DespesasViewSet, basename='despesas')

urlpatterns = [
    path('', include(route.urls)),
    path('receitas/<ano>/<mes>/', ReceitasPorMes.as_view()),
    path('despesas/<ano>/<mes>/', DespesasPorMes.as_view()),
    path('resumo/<ano>/<mes>/', ResumoMes.as_view()),
]
