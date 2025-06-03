from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import DatabaseError, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import InventoryCapture, UserMaster, NextupNumber, DownloadInventory
from .utils import add_inventory
from .export_excel import export_datas_to_excel
import logging

logger = logging.getLogger(__name__)  # For optional logging

def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            request.session['username'] = username

            user = authenticate(request, username=username, password=password)

            if not UserMaster.objects.filter(username=username).exists():
                hashed_password = make_password(password)
                UserMaster.objects.create(username=username, password=hashed_password)
            else:
                user_obj = UserMaster.objects.get(username=username)
                user_obj.save()

            if user:
                login(request, user)
                return redirect('owner')
            else:
                messages.error(request, 'Invalid Username/Password')

        except (DatabaseError, IntegrityError) as db_err:
            messages.error(request, f"Database Error during login: {str(db_err)}")
        except Exception as e:
            messages.error(request, f"Unexpected Login Error: {str(e)}")
            logger.exception("Login error")  # Optional
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            request.session['username'] = username

            if password1 != password2:
                messages.error(request, 'Passwords do not match')
            else:
                from django.contrib.auth.models import User
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already taken')
                else:
                    User.objects.create_user(username=username, password=password1)
                    messages.success(request, 'User created! Please login.')
                    return redirect('login')
        except (DatabaseError, IntegrityError) as db_err:
            messages.error(request, f"Database Error: {str(db_err)}")
        except Exception as e:
            messages.error(request, f"Registration Error: {str(e)}")
            logger.exception("Registration error")
    return render(request, 'register.html')


def owner_view(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')

        if request.method == "POST":
            owner = request.POST.get('owner')
            if not owner:
                messages.error(request, "Please enter owner name")
                return render(request, 'owner.html')
            request.session['owner'] = owner
            return redirect('inventory')
        return render(request, 'owner.html')
    except Exception as e:
        messages.error(request, f"Owner View Error: {str(e)}")
        logger.exception("Owner view error")
        return render(request, 'owner.html')


def inventory_view(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')

        if request.method == "POST":
            owner = request.session.get('owner')
            username = request.user.username
            location = request.POST.get('location')
            sku = request.POST.get("sku")
            uom = request.POST.get('uom')
            case = request.POST.get('case', '')
            status = int(request.POST.get('status', 0))

            try:
                quantity = int(request.POST.get("quantity"))
            except (TypeError, ValueError):
                messages.error(request, "Please enter a valid quantity number")
                return render(request, "Inventory.html")

            InventoryCapture.objects.create(
                owner=owner,
                location=location,
                sku=sku,
                uom=uom,
                quantity=quantity,
                username=username,
                status=status
            )

            record_count = 1
            add_inventory(owner, location, case, sku, uom, record_count, quantity, status, username)

            messages.success(request, "Inventory Captured Successfully!")
            return redirect("inventory")

        return render(request, "Inventory.html")

    except DatabaseError as db_err:
        messages.error(request, f"Database Error: {str(db_err)}")
        logger.exception("Database error in inventory")
    except Exception as e:
        messages.error(request, f"Something went wrong: {str(e)}")
        logger.exception("General error in inventory")
    return render(request, "Inventory.html")


def logout_view(request):
    try:
        logout(request)
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Logout failed: {str(e)}")
        logger.exception("Logout error")
        return redirect('login')


def nextup_number_view(request):
    try:
        nextup = NextupNumber.objects.first()
        if nextup:
            data = {
                "Starting_Number": nextup.Starting_Number,
                "Ending_Number": nextup.Ending_Number,
                "Current_Number": nextup.Current_Number,
                "Next_Number": nextup.Next_Number,
                "Created_Date_IST": nextup.get_created_date_ist(),
                "Updated_Date_IST": nextup.get_updated_date_ist(),
            }
        else:
            data = {"message": "No ASN record found"}
        return JsonResponse(data)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "ASN record does not exist"}, status=404)
    except Exception as e:
        logger.exception("ASN JSON error")
        return JsonResponse({"error": str(e)}, status=500)


def download_inventory_view(request):
    try:
        records = DownloadInventory.objects.all().values()
        return JsonResponse(list(records), safe=False)
    except DatabaseError as db_err:
        logger.exception("Inventory download DB error")
        return JsonResponse({"error": f"Database error: {str(db_err)}"}, status=500)
    except Exception as e:
        logger.exception("Download inventory error")
        return JsonResponse({"error": str(e)}, status=500)


def download_excel_view(request):
    try:
        return export_datas_to_excel(request)
    except Exception as e:
        messages.error(request, f"Download Excel Error: {str(e)}")
        logger.exception("Excel download error")
        return redirect("inventory")
