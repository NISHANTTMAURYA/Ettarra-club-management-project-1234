from django.db import models
from django.contrib.auth.models import User

# customer/models.py
from django.db import models
from django.contrib.auth.models import User
from manager.models import Event

class Seat(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Connect seat to an event
    seat_number = models.CharField(max_length=10, unique=True)  # Ensure unique seat numbers
    is_booked = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)  # To store the locking time
    booked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # Store user who booked the seat
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price of the seat

    def __str__(self):
        status = "Booked" if self.is_booked else "Locked" if self.is_locked else "Available"
        return f"{self.seat_number} - {self.event.title} ({status})"


class Queue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('manager.Event', on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} in queue for {self.event.title}"


# models.py
from django.db import models
from django.contrib.auth.models import User

class QRCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    qr_data = models.CharField(max_length=255, unique=True)  # Unique QR code data
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when it was created

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'qr_data'], name='unique_user_qr')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.qr_data}"
