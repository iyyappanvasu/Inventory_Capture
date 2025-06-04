import pandas as pd
import mysql.connector
from io import BytesIO
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse

def export_datas_to_excel(request):
    mydb = None
    cursor = None

    try:
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='I_iyyappan11',
            database='inventorycapture',
        )
        cursor = mydb.cursor()

        # Read data where download_status = 'no'
        query = """
        SELECT id, asn_number, sku, owner, line_number, Quantity, uom, `case` AS TOID, location 
        FROM inventoryapp_downloadinventory 
        WHERE download_status = 'no'
        """
        df = pd.read_sql(query, mydb)

        if df.empty:
            messages.warning(request, "Sorry, no data found to export!")
            return redirect("inventory")

        # Data Sheet
        df_data = df[['asn_number', 'owner']].drop_duplicates()
        df_data['STATUS'] = 0
        df_data = df_data[['asn_number', 'owner', 'STATUS']]

        data_desc = ['Column Name', 'GenericKey', 'RECEIPTKEY', 'STORERKEY', 'STATUS']
        data_headers = ['Messages', 'GenericKey', 'ASN/Receipt', 'Owner', 'Receipt Status']
        data_rows = [data_desc, data_headers]

        for _, row in df_data.iterrows():
            data_rows.append(['', ''] + row.tolist())
        df_data_final = pd.DataFrame(data_rows, columns=data_headers)

        #  Detail Sheet
        df_detail = df[['asn_number', 'sku', 'owner', 'line_number', 'Quantity', 'uom', 'TOID', 'location']]
        detail_desc = ['Column Name', 'GenericKey', 'RECEIPTKEY', 'SKU', 'STORERKEY',
                       'RECEIPTLINENUMBER', 'QTYEXPECTED', 'UOM', 'TOID', 'TOLOC']
        detail_headers = ['Messages', 'GenericKey', 'ASN/Receipt', 'Item', 'Owner',
                          'Line #', 'Expected Qty', 'UOM', 'LPN', 'Location']
        detail_rows = [detail_desc, detail_headers]

        for _, row in df_detail.iterrows():
            detail_rows.append(['', ''] + row.tolist())
        df_detail_final = pd.DataFrame(detail_rows, columns=detail_headers)

        #  Validations Sheet 
        validation_data = [
            ['Date Format', 'M/d/yy h:mm a', 'MM=Month, dd=Day, yy=Year, mm=Minute, hh=Hour'],
            ['Time Zone', '(GMT-05:00) Eastern Time (US & Canada)', 'America/New_York'],
            ['Empty Fields', '[blank]', 'Put [blank] to remove existing values']
        ]
        df_validations = pd.DataFrame(validation_data)

        #  Write to Excel 
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_data_final.to_excel(writer, index=False, header=False, sheet_name='Data')
            df_detail_final.to_excel(writer, index=False, header=False, sheet_name='Detail')
            df_validations.to_excel(writer, index=False, header=False, sheet_name='Validations')

        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=inventory_data.xlsx'

        #  Update DB Status
        ids = df['id'].tolist()
        if ids:
            format_strings = ','.join(['%s'] * len(ids))
            update_query = f"""
                UPDATE inventoryapp_downloadinventory 
                SET download_status = 'yes' 
                WHERE id IN ({format_strings})
            """
            cursor.execute(update_query, ids)
            mydb.commit()

        return response

    except mysql.connector.Error as err:
        messages.error(request, f"MySQL Error: {err}")
        return redirect("inventory")

    except pd.errors.DatabaseError as db_err:
        messages.error(request, f"Pandas DB Error: {db_err}")
        return redirect("inventory")

    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}")
        return redirect("inventory")

    finally:
        try:
            if cursor:
                cursor.close()
            if mydb and mydb.is_connected():
                mydb.close()
        except Exception:
            pass
