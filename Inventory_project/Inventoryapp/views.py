from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Inventory

def inventory(request):
  if request.method=="POST":
    location=request.POST.get('location')
    sku=request.POST.get("sku")
    case=request.POST.get("case")
    quantity=request.POST.get("quantity")
    
    Inventory.objects.create(
      location=location,
      sku=sku,
      case=case,
      quantity=int(quantity)
    )
    return redirect("success")
  return render (request,"Inventory.html")


def success_page(request):
  return render(request,"success.html")