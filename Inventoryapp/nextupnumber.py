from .models import NextupNumber
from django.db import DatabaseError

def get_next_asn():
    try:
        nextup = NextupNumber.objects.first()

        if not nextup:
            nextup = NextupNumber.objects.create(
                Starting_Number="ASN000001",
                Ending_Number="ASN999999",
                Current_Number="ASN000001",
                Next_Number="ASN000002"
            )

        current_number = nextup.Next_Number
        prefix = "ASN"
        number = int(current_number.replace(prefix, ""))
        next_number = prefix + str(number + 1).zfill(6)

        nextup.Current_Number = current_number
        nextup.Next_Number = next_number
        nextup.save()

        return current_number

    except DatabaseError as e:
        print(f"Database error in nextupnumber.get_next_asn: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in nextupnumber.get_next_asn: {e}")
        return None
