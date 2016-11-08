from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
import django.contrib.auth.models as auth_models
# Create your models here.


class Destination(models.Model):
    coral_code = models.CharField(max_length=255)
    name = models.CharField(max_length=100)


class Hotel(models.Model):
    coral_code = models.CharField(max_length=255)
    name = models.CharField(max_length=100)


class Booking(models.Model):
    STATUS_CHOICES = (
        ('succeeded', 'SUCCEEDED'),
        ('failed', 'FAILED')
    )
    user = models.ForeignKey(auth_models.User)
    provision_code = models.CharField(max_length=255)
    hotel_code = models.CharField(max_length=10)
    booking_code = models.CharField(max_length=255)
    coral_booking_code = models.CharField(max_length=255)
    room_type = models.CharField(max_length=5)
    room_description = models.CharField(max_length=255)
    pax_count = models.IntegerField()
    pax_names = models.TextField()
    status = models.CharField(max_length=9, choices=STATUS_CHOICES)
    price = models.FloatField()

# class User(models.Model):
#     username = models.CharField(max_length=100)
#
#
# class Bookings(models.Model):
#     user = models.ForeignKey(User)
#     book_code = models.CharField(max_length=100)
#     hotel_code = models.CharField(max_length=100)
#     destination_code = models.CharField(max_length=100)
#     checkin = models.DateField()
#     checkout = models.DateField()

