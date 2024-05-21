# from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

# Create your views here.

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

class IndexView(TemplateView):
    template_name = 'index.html'

class SigninView(TemplateView):
    template_name = 'signin.html'

class SignupView(TemplateView):
    template_name = 'signup.html'

class AccountView(TemplateView):
    template_name = 'account.html'
