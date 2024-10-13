from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AdminSignupForm


def admin_signup_view(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            admin_group, created = Group.objects.get_or_create(name='ADMIN')
            admin_group.user_set.add(user)
            messages.success(request, 'Admin account created successfully.')
            return redirect('adminlogin')
        else:
            messages.error(request, 'Error creating account. Please check the details and try again.')
    else:
        form = AdminSignupForm()
    return render(request, 'admin_signup.html', {'form': form})



def admin_login_view(request):
    users_in_group = User.objects.filter(groups__name="ADMIN")
    user_names = [user.username for user in users_in_group]
    
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username in user_names:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/Admin/dashboard/')
                else:
                    messages.error(request, 'User account is not active.')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'admin_login.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')


def admin_logout_view(request):
    logout(request)
    return redirect('/Admin/login')


def admin_graphs(request):
    return render(request, 'admin_graphs.html')


def admin_branches(request):
    return render(request, 'admin_branches.html')


def admin_managers(request):
    return render(request, 'admin_managers.html')
