from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.customer_login_view, name='customerlogin'),
    path('signup/', views.customer_signup_view, name='customersignup'),
    path('dashboard/', views.customer_dashboard_view, name='customerdashboard'),
    path('logout/', views.customer_logout_view, name='customerlogout'),
    path('seats/', views.seats_view, name='seat_list'),  # URL to view the seat layout
    path('select_seat/', views.select_seat, name='select_seat'),  # URL to select a seat
    path('book/', views.book_seat, name='book_seat'), 
    path('booked_seats/', views.booked_seats_view, name='my_booked_seats'),
    path('cancel-booking/<int:seat_id>/', views.cancel_booking, name='cancel_booking'),
    path('join-queue/', views.join_queue, name='join_queue'),
    path('customerevent/', views.customerevent, name ='customerevent'),
    path('mchat/',views.mchat , name='mchat'),
       path('vr_view/', views.vr_view, name ='vr_view'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
]
