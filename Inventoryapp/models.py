from django.db import models
from django.utils import timezone

class InventoryCapture(models.Model):
    owner = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    case = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    uom = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    username = models.CharField(max_length=100, default='default_user')
    created_date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = timezone.now().replace(microsecond=0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} - {self.sku}"


class UserMaster(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_datetime = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        now = timezone.now().replace(microsecond=0)
        if not self.created_date:
            self.created_date = now
        self.updated_datetime = now
        super().save(*args, **kwargs)


class NextupNumber(models.Model):
    Starting_Number = models.CharField(max_length=50)
    Ending_Number = models.CharField(max_length=50)
    Current_Number = models.CharField(max_length=50)
    Next_Number = models.CharField(max_length=50)
    prefix = models.CharField(max_length=10, default='ASN')

    NUMBEROFLINES = models.IntegerField(default=5)  #  Line limit stored in DB

    created_date = models.DateTimeField(blank=True, null=True)
    updated_datetime = models.DateTimeField(blank=True, null=True)
    created_username = models.CharField(max_length=100, blank=True, null=True)
    updated_username = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Current: {self.Current_Number} | Next: {self.Next_Number}"

    def save(self, *args, **kwargs):
        now = timezone.now().replace(microsecond=0)
        if not self.created_date:
            self.created_date = now
        self.updated_datetime = now
        super().save(*args, **kwargs)


class DownloadInventory(models.Model):
    owner = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    case = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    uom = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    asn_number = models.CharField(max_length=20)
    line_number = models.CharField(max_length=6)  # like 000001
    status = models.IntegerField(default=1)
    download_status = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='no')

    def __str__(self):
        return f"{self.asn_number} - {self.line_number}"
