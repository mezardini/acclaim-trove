from django.contrib import admin
from .models import CustomUser, Employee,  Poll, Leaderboard
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Employee)
# admin.site.register(Vote)
admin.site.register(Poll)
admin.site.register(Leaderboard)
