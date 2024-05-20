from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

# User model
class User(models.Model):
    firstName = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True, default='default@default.com')
    password = models.CharField(max_length=128, default=make_password('default_pass'))
    date_registered = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

# Bookmark model
class Bookmark(models.Model):
    date_bookmarked = models.DateField(auto_now_add=True) 
    source = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    url = models.URLField(max_length=200) 
    image_url = models.URLField(max_length=200)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

