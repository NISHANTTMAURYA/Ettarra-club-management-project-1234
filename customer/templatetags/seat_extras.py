# templatetags/seat_extras.py
from django import template
from customer.models import Seat

register = template.Library()

@register.filter
def get_item(seat_id):
    try:
        return Seat.objects.get(id=seat_id).seat_number
    except Seat.DoesNotExist:
        return None
