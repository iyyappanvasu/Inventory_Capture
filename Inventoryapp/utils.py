from .models import DownloadInventory, NextupNumber
from django.db import transaction, DatabaseError
from django.utils import timezone

def add_inventory(owner, location, case, sku, uom, record_count, quantity, status, username):
    try:
        # Start a database transaction
        with transaction.atomic():
            # Get the first record from NextupNumber table
            nextup = NextupNumber.objects.first()

            # If no record exists, initialize with default ASN settings
            if not nextup:
                prefix = "ASN"
                nextup = NextupNumber.objects.create(
                    Starting_Number=f"{prefix}0000001",
                    Ending_Number=f"{prefix}9999999",
                    Current_Number=f"{prefix}0000001",
                    Next_Number=f"{prefix}0000002",
                    prefix=prefix,
                    NUMBEROFLINES=3,
                    created_username=username,
                    updated_username=username,
                    type="ASN"
                )

            # Get the prefix from the database
            prefix = nextup.prefix

            # Extract numeric part from the Current_Number (ignore prefix)
            current_number = int(''.join(filter(str.isdigit, nextup.Current_Number)))

            # Check if the stored prefix in Current_Number is outdated
            current_prefix_in_number = nextup.Current_Number[:3]
            if current_prefix_in_number != prefix:
                current_number += 1  # increment number to continue from previous
                nextup.Current_Number = f"{prefix}{current_number:07d}"
                nextup.Next_Number = f"{prefix}{current_number + 1:07d}"

            last_asn_num = current_number
            MAX_RECORDS_PER_ASN = nextup.NUMBEROFLINES
            total_records = record_count

            # Get the last record with the current ASN number
            last_asn_obj = DownloadInventory.objects.filter(
                asn_number=f"{prefix}{last_asn_num:07d}"
            ).order_by('-line_number').first()

            # Check if owner or max lines reached, then increment ASN
            if last_asn_obj:
                last_owner = last_asn_obj.owner
                last_line_number = int(last_asn_obj.line_number or 0)

                if last_owner != owner or last_line_number >= MAX_RECORDS_PER_ASN:
                    last_asn_num += 1
                    last_line_number = 0
            else:
                last_line_number = 0

            # Add inventory records based on number of lines per ASN
            while total_records > 0:
                if last_line_number < MAX_RECORDS_PER_ASN:
                    remaining = MAX_RECORDS_PER_ASN - last_line_number
                    to_add = min(total_records, remaining)

                    current_asn = f"{prefix}{last_asn_num:07d}"

                    # Create records for the current ASN
                    for i in range(1, to_add + 1):
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
                            status=status,
                            updated_username=username,
                            updated_datetime=timezone.now().replace(microsecond=0),
                        )

                    last_line_number += to_add
                    total_records -= to_add
                else:
                    # Move to next ASN number if current is full
                    last_asn_num += 1
                    last_line_number = 0

            # Update the NextupNumber table with the latest number
            nextup.Current_Number = f"{prefix}{last_asn_num:07d}"
            nextup.Next_Number = f"{prefix}{last_asn_num + 1:07d}"
            nextup.updated_username = username
            nextup.save()

    except DatabaseError as e:
        # Log database-related errors
        print(f"Database error in add_inventory: {e}")
        return False
    except Exception as e:
        # Log any unexpected errors
        print(f"Unexpected error in add_inventory: {e}")
        return False

    return True
