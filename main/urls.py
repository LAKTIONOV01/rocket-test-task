
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'network-nodes', views.NetworkNodeViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/statistics/debt/', views.DebtStatisticsView.as_view(), name='debt-statistics'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]