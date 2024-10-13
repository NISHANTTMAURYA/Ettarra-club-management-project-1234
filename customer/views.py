from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerSignupForm

def customer_signup_view(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
            customer_group.user_set.add(user)
            messages.success(request, 'Account created successfully.')
            return redirect('/customer/login')
        else:
            messages.error(request, 'Error creating account. Please check the details and try again.')
    else:
        form = CustomerSignupForm()
    return render(request, 'customer_signup.html', {'form': form})



from django.contrib.auth import authenticate, login
from django.contrib import messages

def customer_login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.groups.filter(name='CUSTOMER').exists():
                login(request, user)
                return redirect('/customer/dashboard')
            else:
                messages.error(request, 'You are not authorized as a customer.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'customer_login.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def customer_dashboard_view(request):
    return render(request, 'customer_dashboard.html')


from django.contrib.auth import logout
from django.shortcuts import redirect

def customer_logout_view(request):
    logout(request)
    return redirect('/customer/login')




from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Seat
from django.utils import timezone

def seats_view(request):
    seats = Seat.objects.all()  # Fetch all seats
    all_booked = all(seat.is_booked for seat in seats)  # Check if all seats are booked

    return render(request, 'seats_layout.html', {
        'seats': seats,
        'all_booked': all_booked,  # Pass the flag to the template
    })

def select_seat(request):
    if request.method == "POST":
        seat_id = request.POST.get("seat_id")
        seat = Seat.objects.get(id=seat_id)
        
        # Temporarily lock the seat
        seat.is_locked = True
        seat.locked_until = timezone.now() + timezone.timedelta(minutes=1)  # Lock for 1 minute
        seat.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

import json
from django.http import JsonResponse
from .models import Seat

def book_seat(request):
    print("called")
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            selected_seat_ids = data.get('seats', [])  # Get the list of seats

            print("Selected seat IDs:", selected_seat_ids)  # Debugging the received seat IDs

            if selected_seat_ids:  # Ensure there are selected seats
                for seat_id in selected_seat_ids:
                    seat = Seat.objects.get(id=seat_id)
                    if not seat.is_booked:
                        seat.is_booked = True  # Mark seat as booked
                        seat.is_locked = False  # Unlock seat after booking
                        seat.booked_by = request.user  # Store the user who booked the seat
                        seat.save()

                return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



from django.shortcuts import render
from .models import Seat

def booked_seats_view(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        booked_seats = Seat.objects.filter(booked_by=request.user)  # Get seats booked by the current user
    else:
        booked_seats = []  # No seats if the user is not logged in

    return render(request, 'booked_seats.html', {'booked_seats': booked_seats})



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Seat

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *

# def cancel_booking(request, seat_id):
#     if request.method == "POST" and request.user.is_authenticated:  # Check if the user is logged in
#         seat = get_object_or_404(Seat, id=seat_id, booked_by=request.user)  # Ensure the user booked the seat
#         seat.is_booked = False  # Mark seat as available
#         seat.booked_by = None  # Clear the user who booked the seat
#         seat.save()

#         return JsonResponse({'status': 'success'})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authorized'})


# views.py
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Queue
from manager.models import Event

def join_queue(request):
    if request.method == "POST":
        event = get_object_or_404(Event, id=10)
        
        # Get the current queue length for the event to determine the user's position
        current_position = Queue.objects.filter(event=event).count() + 1
        
        # Check if the user is already in the queue
        if Queue.objects.filter(user=request.user, event=event).exists():
            messages.error(request, "You are already in the queue for this event.")
            return redirect('seat_list')  # Redirect to the seats view

        # Create a new queue entry
        queue_entry = Queue.objects.create(user=request.user, event=event, position=current_position)
        
        messages.success(request, f"You have joined the queue! Your position is {current_position}.")
        return redirect('seat_list')  # Redirect back to the seats view
    return redirect('seat_list')  # Redirect for non-POST requests



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Seat, Queue

def cancel_booking(request, seat_id):
    if request.method == 'POST':
        try:
            seat = get_object_or_404(Seat, id=seat_id)
            user = seat.booked_by  # Assuming `booked_by` field exists
            
            # Release the seat
            seat.is_booked = False
            seat.booked_by = None
            seat.save()

            # Check if there are users in the queue
            queue_entry = Queue.objects.filter(event=seat.event).order_by('position').first()
            if queue_entry:
                seat.is_booked = True
                seat.booked_by = queue_entry.user  # Assign the seat to the first user in the queue
                seat.save()

                # Remove the user from the queue
                queue_entry.delete()

                messages.success(request, 'Booking cancelled. The next user in the queue has been assigned the seat.')
            else:
                messages.success(request, 'Booking cancelled successfully.')

        except Exception as e:
            messages.error(request, 'Error cancelling booking. Please try again.')

        return redirect('my_booked_seats')  # Redirect to a page showing the user's bookings
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('my_booked_seats')


from django.shortcuts import render
from manager.models import Event

def customerevent(request):
    events = Event.objects.filter(is_public=True)
    return render(request, 'customerevent.html', {'events': events})

def mchat(request):
    return render(request, 'mchat.html')


def vr_view(request):
    
    return render(request, 'vr_view.html')


# views.py
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO
import base64
from .models import QRCode

@login_required
def generate_qr(request):
    # Create QR code data
    qr_data = "http://127.0.0.1:8000/manager/verified/"

    # Generate a unique QR code for the user
    qr, created = QRCode.objects.get_or_create(user=request.user, qr_data=qr_data)

    if created:
        # If the QR code was created, generate the image
        qr_image = generate_qr_image(qr_data)
        return render(request, 'verification.html', {'qr_image': qr_image})
    else:
        # If the QR code already exists, just display the existing one
        qr_image = generate_qr_image(qr_data)
        return render(request, 'verification.html', {'qr_image': qr_image})

def generate_qr_image(qr_data):
    # Create a QRCode object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()
