from django.urls import path
from . import views

app_name = 'spending'

urlpatterns = [
    path('', views.TitleView.as_view(), name='title'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('index/<int:page>', views.IndexView.as_view(), name='index'),
    path('create/', views.SpendingCreate.as_view(), name='create'),
    path('delete/<int:pk>/', views.SpendingDelete.as_view(), name='delete'),
    path('update/<int:pk>/', views.SpendingUpdate.as_view(), name='update'),
    path('month_dashboard/<int:year>/<int:month>/', views.MonthDashboard.as_view(), name='month_dashboard'),
]