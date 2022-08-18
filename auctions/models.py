from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=64)
    quantity = models.IntegerField(default=0)

    def __str__(self): 
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    price = models.IntegerField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, max_length=64, related_name="MyListings")
    description = models.CharField(max_length=1500, blank=True)
    category = models.ForeignKey(Categories, blank=True, on_delete=models.CASCADE, related_name="allItems")
    picture_url = models.CharField(max_length=300, blank=True)
    watching = models.ManyToManyField(User, blank=True)

    def __str__(self): 
        return f"{self.title[:20]} ({self.seller})"  # how-to f-string the output

class Bids(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="allBids")
    current_bid = models.IntegerField(blank=True)
    top_bid = models.BooleanField(default=False)
    number_of_bids = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, max_length=64)

    def __str__(self):
        return f"Bid # {self.number_of_bids} on {self.listing} : Bid {self.current_bid} $ by {self.winner}."

class Comments(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="allListingComments")
    text = models.CharField(max_length=400, blank=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="AllAutorComments")

    def __str__(self):
        return f"On {self.listing}: '{self.text}' /({self.autor})"