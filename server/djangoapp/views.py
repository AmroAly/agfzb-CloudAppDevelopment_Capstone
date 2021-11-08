from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import *
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def render_static_demplate(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/static_django_template.html', context)

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # if request.method == "GET":
    #     return render(request, 'djangoapp/login.html', context)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)
    

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://4a74f413.us-south.apigw.appdomain.cloud/api/dealerships/dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealerships'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    context['dealer_id'] = dealer_id
    if request.method == "GET":
        
        url = "https://4a74f413.us-south.apigw.appdomain.cloud/api/dealerships/review?dealerId="+str(dealer_id)
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context['reviews'] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)
        # return error message if dealerId is not a nummeric value

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    context = {}
    context['dealer_id'] = dealer_id
    
    if request.user.is_authenticated:
        if request.method == 'GET':
            url = "https://4a74f413.us-south.apigw.appdomain.cloud/api/dealerships/dealerships"
            # Get dealers from the URL
            dealerships = get_dealers_from_cf(url)
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            for dealership in dealerships:
                if dealership.id == dealer_id:
                    context['dealer'] = dealership
            context['cars'] = cars
            return render(request, 'djangoapp/add_review.html', context)
        if request.method == 'POST':
            url = 'https://4a74f413.us-south.apigw.appdomain.cloud/api/dealerships/review'
            review = {}
            # append data to review
            review['id'] = random.randint(100, 1000000000)
            review["time"] = datetime.utcnow().isoformat()
            review['name'] = 'test name'
            review['dealership'] = dealer_id
            review['review'] = request.POST.get('review')
            car = get_object_or_404(CarModel, id=request.POST.get('car'))
            
            review['purchase'] = bool(request.POST.get('purchasecheck', False))
            review['another'] = 'another'
            review['purchase_date'] = request.POST.get('purchasedate')
            review['car_make'] = car.car_make.name
            review['car_model'] = car.name
            review['car_year'] = car.year.strftime("%Y")

            json_data = {}
            json_data['review'] = review
            response = post_request(url, json_payload=json_data, dealer_id=dealer_id)
            return redirect("djangoapp:dealer_reviews", dealer_id=dealer_id)