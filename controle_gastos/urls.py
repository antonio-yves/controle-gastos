from django.urls import path, include
from rest_framework.routers import DefaultRouter
from controle_gastos.views import ReceitasViewSet, DespesasViewSet

route = DefaultRouter()
route.register('receitas', ReceitasViewSet, basename='receitas')
route.register('despesas', DespesasViewSet, basename='despesas')

urlpatterns = [
    path('', include(route.urls))
]
