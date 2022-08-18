from django.contrib import admin

from .models import Categories, User, Listing, Bids, Comments

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Categories)