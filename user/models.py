from django.db import models
from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
# It is recommended to to set up custom user model,
# even when the default user model is sufficient, so
# you can customize user model in the future if the needs arise
# Don't forget to register the models in admin.py
class UserExtended(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)

class Industry(models.Model):
    industry = models.CharField(
        max_length=55, null=False, blank=False
        )
    def __str__(self):
        return self.industry

class CompanyDetail(models.Model):
    username = models.OneToOneField(UserExtended, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=155)
    company_description = models.TextField(max_length=255)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.company_name

# This is unnecessary for now but let's keep it for future use
class UserPreferences(models.Model):
    DARK = 'Dark'
    LIGHT = 'Light'
    UI_MODE = [
        (DARK, 'Dark'),
        (LIGHT, 'Light'),
    ]
    username = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    light_dark_mode = models.CharField(
        max_length=55, default=DARK,
        choices=UI_MODE)

    def __str__(self):
        return f'{self.username}\'s Preferences'
    

#class CompanyIndustry(models.Model):
#    FNB = 'Food and Beverages'
#    DSG = 'Design'
#    IT = 'Technology'
#    OTR = 'Others'
#    INDUSTRIES = [
#        (FNB, 'Food and Beverages'),
#        (DSG, 'Design'),
#        (IT, 'Technology'),
#        (OTR, 'Others'),
#    ]

#    username = models.ForeignKey(UserExtended, on_delete=models.CASCADE)
#
#    industry = models.CharField(
#        max_length=55,
#        choices=INDUSTRIES,
#        default=FNB,
#    )
#
#    def __str__(self):
#        return self.industry
    