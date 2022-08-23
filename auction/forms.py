from django.forms import ModelForm
from .models import Auction, Bid


class AddAuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'image', 'price']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']