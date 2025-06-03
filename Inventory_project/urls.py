from django.urls import path
from Inventoryapp import views

urlpatterns = [
    path('', views.login_view, name='login'),               
    path('register/', views.register_view, name='register'), 
    path('owner/', views.owner_view, name='owner'),          
    path('inventory/', views.inventory_view, name='inventory'),  
    path('logout/', views.logout_view, name='logout'),  
    path('download_inventory/',views.DownloadInventory,name="download_inventory"),
    path('download_excel/',views.download_excel_view, name='download_excel'),
    path('nextup/', views.nextup_number_view, name='nextup-number'),
    path('download-inventory/', views.download_inventory_view, name='download-inventory'),
]


