from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('variables/<int:restricciones>/<int:variables>/<str:method>/', views.variables, name='variables'),
    path('simplex/', views.simplex, name='simplex'),
]