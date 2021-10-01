from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from json import dumps
import datetime
import os
from django.utils.encoding import force_text, smart_str
from django.contrib.auth.models import User
from django import forms

import os
from django.conf import settings

from inventory.models import UserExtras
def handle_uploaded_file(f):  
    with open(os.path.join(settings.MEDIA_ROOT, "user_dp", f.name), 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)

class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()

def main_index(request):
    
    #Show homepage if user is logged in
    if request.user.is_authenticated:
        return render(request, "NH/main_index.html")
    
    #if not logged in show login page
    else:
        return HttpResponseRedirect(reverse("login_view"))

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        toredirect = request.POST.get('toredirect', "")
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if toredirect is "":
                return HttpResponseRedirect(reverse("main_index"))
            else:
                return HttpResponseRedirect(toredirect)
        else:
            return render(request, "NH/login.html", {
                "message": "Invalid username and/or password.",
                "toredirect": toredirect
            })
    else:
        toredirect = request.GET.get('next')
        if toredirect is None:
            toredirect = ""
        return render(request, "NH/login.html",{
            "toredirect": toredirect
        })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login_view"))

def user_list(request):
    return render(request, "NH/user_list.html", {
        "users":User.objects.all()
    })

@login_required(login_url="r'^login/$'")
def development(request):
    return render (request, "NH/development.html") 

@login_required(login_url="r'^login/$'")
def user_info(request):
    if request.method == "POST":
        new_username = request.POST.get('username', "")
        new_firstname = request.POST.get('first_name', "")
        new_lastname = request.POST.get('last_name', "")
        f = request.FILES.get('image', None)
        if new_username == "" or new_firstname =="" or new_lastname=="":
            return render(request, "NH/error.html",{
                "message" : "Ensure all fields are inputed correctly"
            })
        else:
            request.user.username = new_username
            request.user.first_name = new_firstname
            request.user.last_name = new_lastname
            if f != None:
                form = ImageUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    m = UserExtras.objects.get(user=request.user)
                    if bool(m.profilepic) is not False:
                        image_path = m.profilepic.path
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    m.profilepic = form.cleaned_data['image']
                    m.save()
            return render(request, "NH/main_index.html")
    else:
        return render(request, "NH/user_info.html",{
            "user" : request.user
        })