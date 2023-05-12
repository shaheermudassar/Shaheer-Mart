from django.shortcuts import render, redirect
from userauths.forms import UserRegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User
from django.contrib.auth.decorators import login_required
# User = settings.AUTH_USER_MODEL

def register_views(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user=form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, Your account was created successfully. Please create your profile")
            new_user= authenticate(username=form.cleaned_data['email'],
                                   password=form.cleaned_data['password1']
            
            )
            login(request, new_user)
            return redirect("create-profile")
    else:
        print("User cannot be registered")
        form = UserRegistrationForm()

    context = {
        'form': form,
    }

    return render(request, "userauths/signup.html", context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey! You are already logged in...")
        return redirect("/")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user=authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in")
                return redirect("/")
            else:
                messages.warning(request, "User does not exist. Please create an account")
        except:
            messages.warning(request, f"User with {email} does not exist")
        
    return render(request, "userauths/signin.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You logged out")
    return redirect("userauths:signin")

from django.contrib.auth.hashers import check_password

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        user = User.objects.get(email=request.user.email)
        if not check_password(old_password, user.password):
            messages.warning(request, "Old password was incorrect")
        elif confirm_password != new_password:
            messages.warning(request, "Passwords do not match")
        else:
            user.set_password(new_password)
            user.save()
            user = authenticate(request, email=user.email, password=new_password)
            login(request, user)
            messages.success(request, "Password changed successfully")
            return redirect("/")
    return render(request, "userauths/change_password.html")


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        messages.success(request, "Account Deleted Successfully!")
        return redirect("/")

    return render(request, "userauths/delete-account.html")
