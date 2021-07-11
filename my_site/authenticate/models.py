from django.db import models
from django.db.models.fields import BooleanField, DateField, GenericIPAddressField

# Create your models here.


class Post(models.Model):
    Username = models.CharField(max_length=300, unique=True)
    Password = models.CharField(max_length=20)
    Email = models.EmailField()
    ID = models.IntegerField(unique=True)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    activeUser = BooleanField(default=True)

class Logins(models.Model):
    last_visit = models.DateTimeField()
    UserId = models.IntegerField()
    IpAddress = GenericIPAddressField()
    Expires = DateField()
    Successful = BooleanField()