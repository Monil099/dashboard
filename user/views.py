from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required

# Registration view
@login_required
def register_view(request):
    if not request.user.is_superuser:
        return redirect('blog_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, 'msg': 'User Register successfully'})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'blog_list')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    # If form is invalid, it will automatically have the error messages
    return render(request, 'login.html', {'form': form})

# Logout view
def logout_view(request):
    auth_logout(request)
    return redirect('login')
