from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, max_length=64)
    description = models.CharField(max_length=64, blank=True)
    category = models.CharField(max_length=64, blank=True)
    picture_url = models.CharField(max_length=200, blank=True)

    def __str__(self): 
        return f"{self.title[:20]} ({self.seller})"  # how-to f-string the output

class Bids(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="allBids")
    current_bid = models.IntegerField(blank=True)
    number_of_bids = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, max_length=64)

    def __str__(self):
        return f"{self.listing} - current bid is {self.current_bid} by {self.winner}"

class Comments(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="allListingComments")
    text = models.CharField(max_length=400, blank=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="AllAutorComments")

    def __str__(self):
        return f"{self.text} /({self.autor})"