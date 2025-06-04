from django.urls import path
from Inventoryapp import views

urlpatterns = [
    path('', views.login_view, name='login'),          #this url is for the login page     
    path('register/', views.register_view, name='register'),  # this url is register page (backup for future use) 
    path('owner/', views.owner_view, name='owner'), # this url is for the owner page          
    path('inventory/', views.inventory_view, name='inventory'), #this url is for the inventory page
    path('logout/', views.logout_view, name='logout'),  # this url is for the logout button 
    path('download_inventory/',views.DownloadInventory,name="download_inventory"), # this url is for the download inventory (backup for testing)
    path('download_excel/',views.download_excel_view, name='download_excel'), # this url is for the download excel ( for testing)
    path('nextup/', views.nextup_number_view, name='nextup-number'), # this url is to generate the asn number in Nextupnumber table ( for testing)

    #this is for the testing purpose
    path('download-inventory/', views.download_inventory_view, name='download-inventory'),
]


