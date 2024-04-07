from django.contrib import admin
from .models import CustomUser, Nominee, Vote, Poll
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Nominee)
admin.site.register(Vote)
admin.site.register(Poll)
