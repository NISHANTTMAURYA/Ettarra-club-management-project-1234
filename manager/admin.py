from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'manager', 'event_time', 'is_public', 'is_ongoing']
    search_fields = ['title', 'description']
    list_filter = ['is_public', 'is_ongoing']



class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_time', 'is_public', 'is_ongoing')
    search_fields = ('title', 'description')