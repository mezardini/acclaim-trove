from django.contrib import admin
from .models import CustomUser, Nominee, Vote
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Nominee)
admin.site.register(Vote)
