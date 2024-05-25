from django.shortcuts import render
import json
import requests
import logging
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

class NewaportalView(APIView):
    def get(self, request):
        url = ('https://newsapi.org/v2/top-headlines?'
               'country=us&'
               'apiKey=b92aefe2bfb44f199bd1964fb09fa8d7')
        response = requests.get(url)
        data = response.json()
        status = data.get('status')
        return render(request, 'index.html', {'status': status})
        # return Response(status)