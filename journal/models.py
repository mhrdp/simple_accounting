from django.db import models
from django.conf import settings

from user.models import CompanyIndustry

# Create your models here.
class Journal(models.Model):
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )



    def __str__(self):
        return self.username
    