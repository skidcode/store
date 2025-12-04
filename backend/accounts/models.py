from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Extra fields
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Business flags
    email_verified = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=True)

    # Stripe customer ID (optional for future)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username
