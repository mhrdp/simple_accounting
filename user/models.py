from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
# It is recommended to to set up custom user model,
# even when the default user model is sufficient, so
# you can customize user model in the future if the needs arise
# Don't forget to register the models in admin.py
class UserExtended(AbstractUser):
    email = models.EmailField(_('email address'))

class CompanyDetail(models.Model):
    username = models.ForeignKey(UserExtended, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=155)
    company_description = models.TextField(max_length=255)

    def __str__(self):
        return self.company_name
    

class CompanyIndustry(models.Model):
    FNB = 'Food and Beverages'
    DSG = 'Design'
    IT = 'Technology'
    OTR = 'Others'
    INDUSTRIES = [
        (FNB, 'Food and Beverages'),
        (DSG, 'Design'),
        (IT, 'Technology'),
        (OTR, 'Others'),
    ]

    username = models.ForeignKey(UserExtended, on_delete=models.CASCADE)

    industry = models.CharField(
        max_length=55,
        choices=INDUSTRIES,
        default=FNB,
    )

    def __str__(self):
        return self.industry
    