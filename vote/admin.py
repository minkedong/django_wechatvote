from django.contrib import admin
from vote.models import *

class VoteActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )

class VoteImageAdmin(admin.ModelAdmin):
    list_display = ('image', )

admin.site.register(VoteImage, VoteImageAdmin)
admin.site.register(VoteActivity, VoteActivityAdmin)