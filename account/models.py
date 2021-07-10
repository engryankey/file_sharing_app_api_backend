from django.db import models
from django.contrib.auth.models import User

class FireToken(models.Model):
    user = models.OneToOneField(
        User, 
        related_name="token",
        on_delete= models.CASCADE,
        )
    token = models.CharField(
        max_length = 200, 
        blank=True, 
        null=True,
        )
