from django.db import models

# Create your models here.
class WpSite(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    wp_username = models.CharField(max_length=200)
    wp_password = models.CharField(max_length=200)

# WpSite.objects.create(name="White ape", url="https://white-ape-351784.hostingersite.com", wp_username="meetbhingradiya57@gmail.com", wp_password="NC3Q Oqwu tc8o XN82 4Yz6 FATW")