from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    is_dsb = models.BooleanField(default=False)
    is_gf = models.BooleanField(default=False)
    objid = models.BinaryField(default=False, max_length=100)
