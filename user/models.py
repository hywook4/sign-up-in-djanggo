from django.db import models

# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    nickname = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'user'
