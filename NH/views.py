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