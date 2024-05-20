from django.db import models

# Create your models here.

class User(models.Model):
    firstName = models.CharField(max_length=100)
    date_registered = models.DateField()

class Bookmark(models.Model):
    date_bookmarked = models.DateField()
    source = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
