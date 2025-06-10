from django.db import models
from django.utils import timezone

# Model to store captured inventory records
class InventoryCapture(models.Model):
    owner = models.CharField(max_length=100, db_column='OWNER')  # Owner of the inventory
    location = models.CharField(max_length=100, db_column='LOCATION')  # Location of inventory
    case = models.CharField(max_length=100, db_column='CASE')  # Case ID or label
    sku = models.CharField(max_length=100, db_column='SKU')  # Stock Keeping Unit
    uom = models.CharField(max_length=20, db_column='UOM')  # Unit of Measure
    quantity = models.IntegerField(default=1, db_column='QUANTITY')  # Quantity captured
    username = models.CharField(max_length=100, default='default_user', db_column='USERNAME')  # User who captured the entry
    created_date = models.DateTimeField(blank=True, null=True, db_column='ADDDATE')  # Timestamp of creation
    status = models.IntegerField(default=0, db_column='STATUS')  # Status flag (custom usage)

    class Meta:
        db_table = 'INVENTORYCAPTURE'  # Custom table name in database

    def save(self, *args, **kwargs):
        # Automatically set created_date if not set
        if not self.created_date:
            self.created_date = timezone.now().replace(microsecond=0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} - {self.sku}"


# Model to manage users manually (separate from Django's default user model)
class UserMaster(models.Model):
    username = models.CharField(max_length=100, unique=True, db_column='USERNAME')  # Unique username
    password = models.CharField(max_length=100, db_column='PASSWORD')  # Plain or hashed password
    created_date = models.DateTimeField(blank=True, null=True, db_column='ADDDATE')  # User creation time
    updated_datetime = models.DateTimeField(blank=True, null=True, db_column='LASTLOGIN')  # Last login time

    class Meta:
        db_table = 'USERMASTER'

    def save(self, *args, **kwargs):
        # Automatically set created and updated timestamps
        now = timezone.now().replace(microsecond=0)
        if not self.created_date:
            self.created_date = now
        self.updated_datetime = now
        super().save(*args, **kwargs)


# Model to track the ASN number series and line number progress
class NextupNumber(models.Model):
    Starting_Number = models.CharField(max_length=50, db_column='STARTINGNUMBER')  # Start of the ASN series
    Ending_Number = models.CharField(max_length=50, db_column='ENDINGNUMBER')  # End of the ASN series
    Current_Number = models.CharField(max_length=50, db_column='CURRENTNUMBER')  # Last used ASN number
    Next_Number = models.CharField(max_length=50, db_column='NEXTNUMBER')  # Next ASN number to be used
    prefix = models.CharField(max_length=10, default='ASN', db_column='TYPE')  # Prefix for the ASN (like 'ASN')

    NUMBEROFLINES = models.IntegerField(default=0, db_column='NUMBEROFLINES')  # Tracks how many lines used under current ASN

    created_date = models.DateTimeField(blank=True, null=True, db_column='ADDDATE')  # Record creation date
    updated_datetime = models.DateTimeField(blank=True, null=True, db_column='LASTLOGIN')  # Last update time
    created_username = models.CharField(max_length=100, blank=True, null=True, db_column='CREATEDUSERNAME')  # Who created
    updated_username = models.CharField(max_length=100, blank=True, null=True, db_column='UPDATEDUSERNAME')  # Who last updated

    class Meta:
        db_table = 'NEXTUPNUMBER'

    def __str__(self):
        return f"Current: {self.Current_Number} | Next: {self.Next_Number}"

    def save(self, *args, **kwargs):
        # Set timestamps on save
        now = timezone.now().replace(microsecond=0)
        if not self.created_date:
            self.created_date = now
        self.updated_datetime = now
        super().save(*args, **kwargs)


# Model to store finalized inventory data ready for download/export
class DownloadInventory(models.Model):
    owner = models.CharField(max_length=100, db_column='OWNER')  # Owner of the item
    location = models.CharField(max_length=100, db_column='LOCATION')  # Storage location
    case = models.CharField(max_length=100, db_column='CASE')  # Case identifier
    sku = models.CharField(max_length=100, db_column='SKU')  # SKU of the item
    uom = models.CharField(max_length=20, db_column='UOM')  # Unit of Measure
    quantity = models.IntegerField(default=1, db_column='QUANTITY')  # Quantity captured
    asn_number = models.CharField(max_length=20, db_column='ASNNUMBER')  # ASN number linked to this entry
    line_number = models.CharField(max_length=6, db_column='LINENUMBER')  # Line number under the ASN
    status = models.IntegerField(default=1, db_column='STATUS')  # Current status of the item
    download_status = models.CharField(
        max_length=3,
        choices=[('yes', 'Yes'), ('no', 'No')],
        default='no',
        db_column='DOWNLOADSTATUS'
    )  # Flag to track if data is downloaded

    class Meta:
        db_table = 'DOWNLOADINVENTORY'

    def __str__(self):
        return f"{self.asn_number} - {self.line_number}"
