from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    event_date = models.DateField()  # Event Date
    event_time = models.TimeField()  # Event Time
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    is_ongoing = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    number_of_seats = models.PositiveIntegerField(default=0)  # Number of seats for the event
    photo_url = models.URLField(max_length=300, blank=True, null=True)  # Photo URL

    def __str__(self):
        return self.title


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the event first
        self.create_seats()  # Create seats after saving the event

    def create_seats(self):
        from customer.models import Seat
        print(f"Creating seats for event: {self.title} with {self.number_of_seats} seats.")
        for seat_number in range(1, self.number_of_seats + 1):
            seat, created = Seat.objects.get_or_create(
                event=self,
                seat_number=f"S{seat_number:03d}",
            )
            if created:
                print(f"Seat {seat.seat_number} created for event {self.title}.")
            else:
                print(f"Seat {seat.seat_number} already exists.")

