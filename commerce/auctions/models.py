from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


LISTING_STATUS = (
    ('active', 'Active'),
    ('closed', 'Closed'),
)


class Listing(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_bid = models.FloatField()
    status = models.CharField(max_length=10, choices=LISTING_STATUS, default='active')
    creation_date = models.DateTimeField(default=timezone.now)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_listings', blank=True, null=True)

    def __str__(self):
        return self.title


class Bid(models.Model):
    listing_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.value}"


class Comment(models.Model):
    listing_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing_item.title}"
