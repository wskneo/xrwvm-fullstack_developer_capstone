# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_request(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            logger.info(f"User '{username}' has logged out.")
            return JsonResponse({"status": "Logged out", "userName": ""})
        else:
            return JsonResponse({"status": "No active session"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})


# from django.shortcuts import render
# from .models import Dealership  # Assuming you have a Dealership model

# def get_dealerships(request):
#     try:
#         dealerships = Dealership.objects.all()
#         context = {"dealership_list": dealerships}
#         return render(request, "index.html", context)
#     except Exception as e:
#         logger.error(f"Error fetching dealerships: {str(e)}")
#         return render(request, "index.html", {"dealership_list": [], "error": "Unable to load dealerships."})


# from django.shortcuts import render
# from .models import DealerReview  # Assuming you have a DealerReview model

# def get_dealer_reviews(request, dealer_id):
#     try:
#         reviews = DealerReview.objects.filter(dealer_id=dealer_id)
#         context = {
#             "dealer_id": dealer_id,
#             "reviews": reviews
#         }
#         return render(request, "dealer_reviews.html", context)
#     except Exception as e:
#         logger.error(f"Error fetching reviews for dealer {dealer_id}: {str(e)}")
#         return render(request, "dealer_reviews.html", {
#             "dealer_id": dealer_id,
#             "reviews": [],
#             "error": "Unable to load dealer reviews."
#         })


# from django.shortcuts import render, get_object_or_404
# from .models import Dealership  # Assuming you have a Dealership model

# def get_dealer_details(request, dealer_id):
#     try:
#         dealer = get_object_or_404(Dealership, id=dealer_id)
#         context = {
#             "dealer": dealer
#         }
#         return render(request, "dealer_details.html", context)
#     except Exception as e:
#         logger.error(f"Error fetching dealer details for ID {dealer_id}: {str(e)}")
#         return render(request, "dealer_details.html", {
#             "dealer": None,
#             "error": "Unable to load dealer details."
#         })


# Create a `add_review` view to submit a review
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from .models import DealerReview, Dealership  # Assuming these models exist
# import json

# @csrf_exempt
# def add_review(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)

#             dealer_id = data.get('dealer_id')
#             reviewer_name = data.get('reviewer_name')
#             comment = data.get('comment')
#             rating = data.get('rating')

#             # Validate input
#             if not all([dealer_id, reviewer_name, comment, rating]):
#                 return JsonResponse({"error": "Missing required fields"}, status=400)

#             # Optional: Validate dealer exists
#             dealership = Dealership.objects.filter(id=dealer_id).first()
#             if not dealership:
#                 return JsonResponse({"error": "Dealer not found"}, status=404)

#             # Save the review
#             review = DealerReview.objects.create(
#                 dealer_id=dealer_id,
#                 reviewer_name=reviewer_name,
#                 comment=comment,
#                 rating=rating
#             )
#             review.save()

#             return JsonResponse({"status": "Review submitted successfully", "review_id": review.id})
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#         except Exception as e:
#             logger.error(f"Error submitting review: {str(e)}")
#             return JsonResponse({"error": "Server error"}, status=500)
#     else:
#         return JsonResponse({"error": "Invalid request method"}, status=405)