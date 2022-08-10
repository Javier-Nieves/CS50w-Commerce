from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bids, Comments


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "bids": Bids.objects.all()
    })


def create_view(request):
    # setting types for listings
    typeList = ["flowers", "trees"]  # TODO

    # creating new listing 
    if request.method == "POST":
        title = request.POST.get("title")
        price = request.POST.get("price")
        description = request.POST.get("description")
        category = request.POST.get("category")
        seller = User.objects.get(username=request.user.username)
        picture_url = request.POST.get("image-url")
        Listing.objects.create(title=title, price=price, seller=seller, description=description, picture_url=picture_url)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "categories": typeList
    })

# link from index leads to /{{title}} page, and Urls take this title from url bar and send the user to this function
def listing_view(request, title):
    # geting all DB entry's parameters
    desc = Listing.objects.filter(title=title).all()
    bids = Bids.objects.filter(listing__title=title).values()  # filtration by foreign key ??
    coms = Comments.objects.filter(listing__title=title).all()
    # top - "if user is a highest bidder"
    try:
        # check if user is the highest bidder on this listing
        if request.user.is_authenticated and (request.user.username ==
        Bids.objects.filter(listing__title=title).values('winner__username').first()['winner__username']):
            top = "yes"
        else:
            top = "no"
    except:
        top = "no"
    if request.method == "POST":
        # if new bid is made - go to function Bid
        if request.POST.get("bid-button", None):
            new_bid = int(request.POST.get("bid"))
            return listing_view_bid(request, title, desc, bids, top, new_bid, coms)
        # if new comment is made - go to function Comment
        elif request.POST.get("comment", None):
            return listing_view_comment(request, title, desc, bids, top, coms)
    # GET
    else:
        return show_page(request, desc, bids, "", top, coms)

def listing_view_bid(request, title, desc, bids, top, new_bid, coms):
    if request.user.is_authenticated:
        # if user is seller
        name = Listing.objects.filter(title=title).values('seller__username').first()['seller__username'] # a way to get parameters from queryset
        if request.user.username == name:  # selects the first position in queryset (desc)
            return show_page(request, desc, bids, "Can't buy your own item", top, coms)

        # new higher bid
        if new_bid > Listing.objects.filter(title=title).values().first()['price']:  # ho to get value from model
            if not first_bid(title):
                if new_bid > bids.first()['current_bid']: 
                    bid_update = Bids.objects.get(listing=Listing.objects.get(title=title))
                    bid_update.number_of_bids += 1
                    bid_update.winner = User.objects.get(username=request.user.username) # get_username()
                    bid_update.current_bid = new_bid
                    bid_update.save()
                    return show_page(request, desc, bids, "Successful bid!", "yes", coms)
                else:
                    return show_page(request, desc, bids, "Bid is too low", top, coms)
            # if first bid
            else:
                # create new Bid instance (!)
                create_bid = Bids(
                    listing=Listing.objects.get(title=title),
                    winner=User.objects.get(username=request.user.username),
                    number_of_bids=1,
                    current_bid=new_bid)
                # save is needed for new Bid to be in DB
                create_bid.save()
                return show_page(request, desc, bids, "Successful bid!", "yes", coms)
        # small bid
        else:
            return show_page(request, desc, bids, "Bid is too low", top, coms)
    # if not autentificated
    else:
        return show_page(request, desc, bids, "You are not autenticated. Please log in.", "no", coms)


def listing_view_comment(request, title, desc, bids, top, coms):
    new_comment = request.POST.get("comment")
    create_comment = Comments(
        listing=Listing.objects.get(title=title),
        text=new_comment,
        autor=User.objects.get(username=request.user.username))
    create_comment.save()
    return show_page(request, desc, bids, "", top, coms)

# ----------------Functions:

def first_bid(title):
    bids = Bids.objects.filter(listing__title=title).values()
    try:
        bids.first()['current_bid']
        return False
    except:
        return True

def show_page(request, desc, bids, message, top, coms):
    return render(request, "auctions/view.html", {
                "desc": desc,
                "bids": bids,
                "message": message,
                "top": top,
                "coms": coms
                })

# ----------------LOGIN and friends

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")