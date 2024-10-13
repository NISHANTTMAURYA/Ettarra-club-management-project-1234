from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.manager_login_view, name='managerlogin'),
    path('signup/', views.manager_signup_view, name='managersignup'),
    path('dashboard/', views.manager_dashboard_view, name='managerdashboard'),
    path('logout/', views.manager_logout_view, name='managerlogout'),
    path('create_event/', views.create_event, name='createevent'),
    path('events/',views.event_list_view, name='eventlist'),  # Ensure this points to the correct view
    path('events/end/<int:event_id>/', views.end_event_view, name='endevent'),
 
   
    path('cafe-events-planning/', views.cafe_events_planning, name='cafe_events_planning'),
    path('dashboard/', views.dashboard , name ='dashboard'),
    path('event/',views.event,name='event'),
    path('endedevent/', views.endedevent ,name='endedevent'),
    path('events-price/', views.list_events, name='list_events'),
    path('assign-seat-prices/<int:event_id>/', views.assign_seat_prices, name='assign_seat_prices'),
    path('massmail/', views.massmail, name='massmail'),
    path('download-excel-template/', views.download_excel_template, name='download_excel_template'),
    path('oneononechat/', views.oneononechat, name='oneoneonechat'),
 
    path('verified/', views.verified, name='verified'),
]