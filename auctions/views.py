from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bids, Comments, Categories


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "bids": Bids.objects.all()
    })

@login_required  # creating new listing
def create_view(request):
    # creating new listing
    if request.method == "POST":
        title = request.POST.get("title")
        if not Listing.objects.filter(title=title):
            price = request.POST.get("price")
            description = request.POST.get("description")
            try:
                category = Categories.objects.get(category=request.POST.get("category"))
            except:
                category = Categories.objects.get(category="None")
            seller = User.objects.get(username=request.user.username)
            picture_url = request.POST.get("image-url")
            Listing.objects.create(title=title, price=price, seller=seller, description=description, picture_url=picture_url, category=category)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "message": "Listing's name is not unique"
            })
    return render(request, "auctions/create.html", {
        "categories": Categories.objects.all()
    })

@login_required
def edit_view(request, title):
    if request.method == "POST":
        list_edit = Listing.objects.get(title=title)
        list_edit.price = request.POST.get("price")
        list_edit.description = request.POST.get("description")
        try:
            list_edit.category = Categories.objects.get(category=request.POST.get("category"))
        except:
            list_edit.category = Categories.objects.get(category="None")
        list_edit.seller = User.objects.get(username=request.user.username)
        list_edit.picture_url = request.POST.get("image-url")
        list_edit.save()
        return HttpResponseRedirect(reverse('view', kwargs={'title': title}))  # redirect with parameter
    return render(request, "auctions/edit.html", {
        "listing": Listing.objects.filter(title=title, seller=User.objects.get(username=request.user.username)).all(),
        "categories": Categories.objects.all()
    })


# link from index leads to /{{title}} page, and Urls take this title from url bar and send the user to this function
def listing_view(request, title):
    # geting all DB entry's parameters
    desc = Listing.objects.filter(title=title).all()
    bids = Bids.objects.filter(listing__title=title).order_by("-number_of_bids")[:1]  # filtration by foreign key ??
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
            if not request.POST.get("bid"):
                return show_page(request, desc, bids, "", top, coms)
            new_bid = int(request.POST.get("bid"))
            return listing_view_bid(request, title, desc, bids, top, new_bid, coms)

        # if watchlist is activated:
        elif request.POST.get("watchlist-button", None):
            Watcher(request, title, "add")
            return show_page(request, desc, bids, "", top, coms)
        elif request.POST.get("remove-watchlist-button", None):
            Watcher(request, title, "remove")
            return show_page(request, desc, bids, "", top, coms)
        elif request.POST.get("remove-watchlist-outer-call", None):
            Watcher(request, title, "remove")
            return HttpResponseRedirect(reverse("watchlist")) 

        # if listing is beeng edited by owner
        elif request.POST.get("edit-button", None):
            return HttpResponseRedirect(reverse('edit', kwargs={'title': title}))

        # if listing is being closed by owner
        elif request.POST.get("close-button", None):
            close_listing = Listing.objects.get(title=title)
            close_listing.active = False
            close_listing.save()
            return show_page(request, desc, bids, "Your auction is closed.", top, coms)

        # if new comment is made - go to function Comment
        else:
            if not request.POST.get("comment"):
                return show_page(request, desc, bids, "", top, coms)
            return listing_view_comment(request, title, desc, bids, top, coms)
        
    # GET
    else:
        return show_page(request, desc, bids, "", top, coms)


@login_required  # making a bid on listing
def listing_view_bid(request, title, desc, bids, top, new_bid, coms):
    # new higher bid
    if new_bid > Listing.objects.filter(title=title).values().first()['price']:  # how to get value from model
        if not first_bid(title):
            if new_bid > bids.values()[0]['current_bid']:
                # previous bid is no longer the highest
                old_bid_update = Bids.objects.get(listing=Listing.objects.get(title=title), top_bid=True)
                old_bid_update.top_bid = False
                old_bid_update.save()
                # create new highest bid
                new_number = bids.values()[0]['number_of_bids'] + 1
                Bids.objects.create(listing=Listing.objects.get(title=title), winner=User.objects.get(username=request.user.username), 
                current_bid=new_bid, number_of_bids=new_number, top_bid=True)
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
                current_bid=new_bid,
                top_bid = True)
            # save is needed for new Bid to be in DB
            create_bid.save()
            return show_page(request, desc, bids, "Successful bid!", "yes", coms)
    # small bid
    else:
        return show_page(request, desc, bids, "Bid is too low", top, coms)
    

@login_required  # comment creation
def listing_view_comment(request, title, desc, bids, top, coms):
    if request.user.is_authenticated:
        new_comment = request.POST.get("comment")
        create_comment = Comments(
            listing=Listing.objects.get(title=title),
            text=new_comment,
            autor=User.objects.get(username=request.user.username))
        create_comment.save()
        return show_page(request, desc, bids, "", top, coms)


@login_required  # watchlist function
def watchlist_view(request):
    watchlist = Listing.objects.filter(watching__username=request.user.username)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "bids": Bids.objects.all()
    })


@login_required
def closed_view(request):
    return render(request, "auctions/closed.html", {
        "listings": Listing.objects.all(),
        "bids": Bids.objects.all()
    })


def all_categories(request):
    for cat_change in Categories.objects.all():
        cat_count = Listing.objects.filter(category=cat_change, active=True).count()
        cat_change.quantity = cat_count
        cat_change.save()
    return render(request, "auctions/allcategories.html", {
        "categories": Categories.objects.all()
    })


def category_list(request, category_name):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.all(),
        "categories": Categories.objects.filter(category=category_name).all()
    })
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

def Watcher(request, title, action):
    # how to edit ManyToMany field. Get the needed model, create variable for it
    watchlist_alter = Listing.objects.get(title=title)
    # save the variable
    watchlist_alter.save()
    # create a variable for the thing you want to insert to MtM field
    watching = User.objects.get(username=request.user.username)
    # save it as well
    watching.save()
    if action == "add":
        # insert second var into the first var
        watchlist_alter.watching.add(watching)
    elif action == "remove":
        watchlist_alter.watching.remove(watching)
    return True

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