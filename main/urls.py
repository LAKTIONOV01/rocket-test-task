from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'network-nodes', views.NetworkNodeViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/statistics/debt/', views.DebtStatisticsView.as_view(), name='debt-statistics'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'api/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
