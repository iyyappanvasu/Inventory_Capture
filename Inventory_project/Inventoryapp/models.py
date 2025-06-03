from django.db import models

class Inventory(models.Model):
  location=models.CharField(max_length=50,default="")
  sku=models.CharField(max_length=50,default="")
  case=models.CharField(max_length=50,default="")
  quantity=models.IntegerField(default=0)