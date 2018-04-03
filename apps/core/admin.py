from django.contrib import admin
from apps.core import models

# Register your models here.

admin.site.register(models.Event)
admin.site.register(models.Hour)
admin.site.register(models.Holiday)
admin.site.register(models.NonWorkingDay)
admin.site.register(models.Profession)
admin.site.register(models.Profile)
admin.site.register(models.Status)
admin.site.register(models.Turn)
