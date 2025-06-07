from .models import DownloadInventory, NextupNumber
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError

User = get_user_model()

def add_inventory(owner, location, case, sku, uom, record_count, quantity, status, username):
    """
    Handles inventory insertion and ASN generation logic.
    Uses max_records_per_asn limit from DB.
    """
    try:
        with transaction.atomic():
            #  Load ASN tracking data or create new if not exists
            nextup = NextupNumber.objects.first()
            if not nextup:
                nextup = NextupNumber.objects.create(
                    Starting_Number="ASN0000001",
                    Ending_Number="ASN9999999",
                    Current_Number="ASN0000001",
                    Next_Number="ASN0000002",
                    prefix="ASN",
                    NUMBEROFLINES=0, #it determines number of lines(limit of the asn) 
                    created_username=username,
                    updated_username=username
                )

            MAX_RECORDS_PER_ASN = nextup.NUMBEROFLINES
            prefix = nextup.prefix
            total_records = record_count

            #  Get last ASN info
            last_asn_obj = DownloadInventory.objects.order_by('-asn_number', '-line_number').first()
            if last_asn_obj and last_asn_obj.asn_number:
                last_owner = last_asn_obj.owner # Getting owner in this
                asn_str = last_asn_obj.asn_number

                if asn_str.startswith(prefix):
                    num_part = asn_str[len(prefix):]
                    last_asn_num = int(num_part) if num_part.isdigit() else 1
                else:
                    last_asn_num = 1

                last_line_number = int(last_asn_obj.line_number) if last_asn_obj.line_number else 0

                if last_owner != owner: # owner validation
                    last_asn_num += 1
                    last_line_number = 0
            else:
                last_asn_num = 1
                last_line_number = 0

            #  Add inventory records
            while total_records > 0:
                if last_line_number < MAX_RECORDS_PER_ASN:
                    remaining_space = MAX_RECORDS_PER_ASN - last_line_number
                    records_to_add = min(total_records, remaining_space)

                    current_asn = f"{prefix}{last_asn_num:07d}"

                    for i in range(1, records_to_add + 1):
                        line_number = last_line_number + i
                        DownloadInventory.objects.create(
                            owner=owner,
                            location=location,
                            case=case,
                            sku=sku,
                            uom=uom,
                            quantity=quantity,
                            asn_number=current_asn,
                            line_number=f"{line_number:05d}",
                            status=status
                        )

                    last_line_number += records_to_add
                    total_records -= records_to_add
                else:
                    last_asn_num += 1
                    last_line_number = 0

            #  Update ASN tracking
            nextup.Current_Number = f"{prefix}{last_asn_num:07d}"
            nextup.Next_Number = f"{prefix}{last_asn_num + 1:07d}"
            nextup.updated_username = username
            nextup.save()

    except DatabaseError as e:
        print(f"Database error in add_inventory: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in add_inventory: {e}")
        return False

    return True


def get_next_asn(user_id):
    """
    Retrieves the next available ASN number and updates the ASN tracking model.
    """
    try:
        nextup = NextupNumber.objects.first()
        if not nextup:
            nextup = NextupNumber.objects.create(
                Starting_Number="ASN000001",
                Ending_Number="ASN999999",
                Current_Number="ASN000001",
                Next_Number="ASN000002",
                prefix="ASN",
                NUMBEROFLINES=5
            )

        current_number = nextup.Next_Number
        prefix = nextup.prefix or "ASN"
        number = int(current_number.replace(prefix, ""))
        next_number = prefix + str(number + 1).zfill(6)

        nextup.Current_Number = current_number
        nextup.Next_Number = next_number

        try:
            user = User.objects.get(pk=user_id)
            username = user.username
        except User.DoesNotExist:
            username = "unknown"

        if not nextup.created_username:
            nextup.created_username = username
        nextup.updated_username = username

        nextup.save()
        return current_number

    except DatabaseError as e:
        print(f"Database error in get_next_asn: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_next_asn: {e}")
        return None
