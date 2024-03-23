from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True)


class Listing(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.FloatField()
    creation_date = models.DateTimeField(default=timezone.now)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Bid(models.Model):
    listing_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bid of {self.value} on {self.listing_item.title}"


class Comment(models.Model):
    listing_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing_item.title}"
