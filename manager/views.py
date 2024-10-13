from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from customer.models import Seat
from django.http import HttpResponse, FileResponse

def manager_signup_view(request):
    if request.method == 'POST':
        form = ManagerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            manager_group, created = Group.objects.get_or_create(name='MANAGER')
            manager_group.user_set.add(user)
            messages.success(request, 'Manager account created successfully.')
            return redirect('managerlogin')
        else:
            messages.error(request, 'Error creating account. Please check the details and try again.')
    else:
        form = ManagerSignupForm()
    return render(request, 'manager_signup.html', {'form': form})


from django.contrib.auth import authenticate, login
from django.contrib import messages

def manager_login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.groups.filter(name='MANAGER').exists():
                login(request, user)
                return redirect('/manager/dashboard')
            else:
                messages.error(request, 'You are not authorized as a manager.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'manager_login.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.shortcuts import render
from .models import Event
from django.contrib.auth.decorators import login_required

@login_required
def manager_dashboard_view(request):
    events = Event.objects.filter(manager=request.user)  # Only show events created by the logged-in manager
    return render(request, 'managerdashboard.html', {'events': events})



from django.contrib.auth import logout
from django.shortcuts import redirect

def manager_logout_view(request):
    logout(request)
    return redirect('/manager/login')



@login_required
def create_event(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        
        # Convert number_of_seats to integer
        number_of_seats = int(request.POST.get('number_of_seats'))  # Convert to integer
        
        # Create the event
        event = Event.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            event_time=event_time,
            manager=request.user,
            number_of_seats=number_of_seats  # Use the integer value
        )

        # Call create_seats to generate seats
        event.create_seats()

        return redirect('managerdashboard')  # Redirect after event creation

    return render(request, 'create_event.html')
 # Render form if not a POST request


from twilio.rest import Client

@login_required
def end_event_view(request, event_id):
    try:
        event = Event.objects.get(id=event_id, manager=request.user)
        event.is_ongoing = False
        event.save()
        messages.success(request, 'Event ended successfully.')
        
        account_sid = 'ACb604cdff6ba558c3c2b0c563a69a9a02'
        auth_token = '1633d5d0f6d0eaeec236ba96af72b62b'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to='+919137796495',
            from_='+18577676358',
            body='ETTARA: \nThe Event Has Ended Please Submit Your Review By Clicking The Below Link\n127.0.0.1:8000/review',
            )
    except Event.DoesNotExist:
        messages.error(request, 'Event not found or you are not authorized to end it.')
    return redirect('/manager/events/')  # Ensure this is the name of your dashboard URL



def event_list_view(request):
    events = Event.objects.filter(is_public=True, is_ongoing=True).order_by('event_time')
    return render(request, 'event_list.html', {'events': events})





@login_required
def endedevent(request):
    events = Event.objects.filter(is_ongoing=False).order_by('event_time')  # Fetch ended events
    return render(request, 'endedevent.html', {'events': events})  # Pass the events to the template



import os
from dotenv import load_dotenv
import google.generativeai as genai
from django.shortcuts import render
from PyPDF2 import PdfReader
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import HttpResponse
from fpdf import FPDF

# Load environment variables
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Generation configuration for Gemini AI
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Helper function to extract text from a PDF
def extract_pdf_data(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Helper function to generate a PDF report
def generate_pdf_report(response_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add response text to the PDF
    for line in response_text.split("\n"):
        pdf.cell(0, 10, txt=line, ln=True)
    
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, "event_plan_report.pdf")
    pdf.output(pdf_file_path)

    return pdf_file_path

# View to handle event planning request and AI response
def cafe_events_planning(request):
    response_text = ""
    
    if request.method == "POST":
        # Handle PDF file upload
        uploaded_pdf = request.FILES.get("event_data_pdf", None)
        
        if uploaded_pdf:
            # Save uploaded PDF temporarily using Django's default storage
            pdf_file_path = default_storage.save(f'tmp/{uploaded_pdf.name}', uploaded_pdf)
            pdf_full_path = os.path.join(settings.MEDIA_ROOT, pdf_file_path)
            
            # Extract data from the uploaded PDF
            pdf_text = extract_pdf_data(pdf_full_path)
            
            # Formulate the user input using the extracted PDF data
            user_input = (
               f"Using the café event data from the past week, please create a detailed event plan for the upcoming week. "
    f"Only include the events listed in the data provided, ensuring that the plan considers the following: "
    f"profitability, customer preferences, booking trends, demographics (age, gender), potential for overbooking, "
    f"and expenses from last week's events.\n"
    f"Here is the data from last week:\n{pdf_text}\n\n"
    f"For each event, please specify the date and time, target audience, estimated costs, and any promotional strategies "
    f"that could enhance attendance and profitability."
            )
            
            # Generate AI response using Gemini
            try:
                # Initialize the model and chat session
                model = genai.GenerativeModel(
                    model_name="gemini-1.0-pro",
                    generation_config=generation_config,
                )
                chat_session = model.start_chat(history=[])

                # Send user input to the AI and get the response
                response = chat_session.send_message(user_input)
                response_text = response.text

                # Generate a PDF report
                pdf_file_path = generate_pdf_report(response_text)
                
            except Exception as e:
                response_text = f"An error occurred during AI generation: {str(e)}"
    
    # Render the AI response in the template
    context = {
        'response': response_text,
        'pdf_file_path': pdf_file_path if 'pdf_file_path' in locals() else None,
    }
    return render(request, 'ai.html', context)


def dashboard(request):
    return render (request, 'managerdashboard.html')


def event(request):
    return render(request, 'managerevent.html')

def events(request):
    return render(request, 'event_list.html')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def assign_seat_prices(request, event_id):
    # Get the event for which to assign seat prices
    event = get_object_or_404(Event, id=event_id)
    seats = Seat.objects.filter(event=event)

    if request.method == "POST":
        # Update prices for each seat based on form input
        for seat in seats:
            price_key = f'price_{seat.id}'
            price_value = request.POST.get(price_key)
            if price_value:
                # Assuming you have a price field in your Seat model
                seat.price = float(price_value)  # or Decimal(price_value) if using DecimalField
                seat.save()

        return redirect('managerdashboard')  # Redirect after updating prices

    return render(request, 'assign_seat_prices.html', {'event': event, 'seats': seats})


def list_events(request):
    events = Event.objects.all()  # Fetch all events
    return render(request, 'list_events.html', {'events': events})


from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import os

from django.contrib import messages

from django.contrib import messages

def massmail(request):
    if request.method == 'POST':
        # File upload
        excel_file = request.FILES.get('excel_file')
        email_subject = request.POST.get('email_subject')
        email_body_template = request.POST.get('email_body')

        if not excel_file or not email_subject or not email_body_template:
            return HttpResponse("Please upload all required fields and provide email content.")

        # Save uploaded Excel file
        fs = FileSystemStorage()
        excel_path = fs.save(excel_file.name, excel_file)

        # Read the Excel file
        try:
            df = pd.read_excel(
                os.path.join(settings.MEDIA_ROOT, excel_path),
                sheet_name="Guests",  # Update sheet name if needed
                na_values=""
            )
        except Exception as e:
            return HttpResponse(f"Error reading Excel file: {e}")

        # Track if all emails were sent successfully
        all_emails_sent = True

        # Save uploaded invitation files (if any)
        invitation_files = request.FILES.getlist('invitation_files')

        # Send email to each student
        for _, row in df.iterrows():
            try:
                student_name = row['Student Name']
                student_email = row['Student Email ID']
                student_phone = row['Student Phone No']

                # Convert student_phone to string
                student_phone_str = str(student_phone)

                # Replace placeholders in email body
                email_body = email_body_template.replace('{{student_name}}', student_name).replace('{{student_phone}}', student_phone_str)

                # HTML email content
                html_body = f"""
                <html>
                <body>
                    <p>{email_body}</p>

                    <br>

                    <p>Best Regards,<br>
                    <strong>The Event Team</strong></p>
                </body>
                </html>
                """

                # Create the email message
                email = EmailMessage(
                    email_subject,
                    html_body,
                    settings.DEFAULT_FROM_EMAIL,  # Use a default email from settings
                    [student_email],
                )
                email.content_subtype = 'html'  # Set the email content type to HTML

                # Attach invitation files if any
                for invitation_file in invitation_files:
                    email.attach(invitation_file.name, invitation_file.read(), invitation_file.content_type)

                # Send the email
                email.send()
                print(f"Invitation sent to {student_email}")
            except Exception as e:
                print(f"Failed to send email to {student_email}: {e}")
                all_emails_sent = False  # Set the flag to False if any email fails

        # Add a success message only if all emails were sent successfully
        if all_emails_sent:
            messages.success(request, "Mails sent successfully!")
        else:
            messages.error(request, "Some mails failed to send. Please check the logs.")

    # Render the upload invitations template
    return render(request, 'massmail.html')






from django.http import FileResponse
from django.conf import settings
import os

def download_excel_template(request):
    # Path to the Excel template in the static directory
    file_path = os.path.join(settings.BASE_DIR, 'static', 'standard_template.xlsx')  # Adjust the path as necessary
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='standard_template.xlsx')



def oneononechat(request):
    return render(request, 'oneononechat.html')


# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def verified(request):
    return render(request, 'verified.html')

# comment

