from django.db import models
from django.contrib.auth.models import User


class Auction(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(null=True)
    seller = models.ForeignKey(User, related_name='seller', null=True, default=None, on_delete=models.CASCADE)

    # sell data
    sold = models.BooleanField(default=False)
    buyer = models.ForeignKey(User, null=True, default=None, related_name='buyer', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, null=True, decimal_places=2, default=0)


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)