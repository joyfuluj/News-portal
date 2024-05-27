from django.shortcuts import render
import json
import requests
import logging
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

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
        articles = data.get('articles')
        detail = self.getDetails(articles)
        return render(request, 'index.html', {'status': detail})
        # return Response(detail)
    
    def getDetails(self, articles):
        detail_list = []
        for article in range(1,len(articles)):
            item = articles[article]
            date_published = item.get('publishedAt')
            date_part = ""
            if date_published:
                datetime_obj = datetime.strptime(date_published, "%Y-%m-%dT%H:%M:%SZ")
                date_part = datetime_obj.date()
            detail = {
                'source' : item.get('source').get('name'),
                'title' : item.get('title'),
                'url' : item.get('url'),
                'image_url' : item.get('urlToImage'),
                'content' : item.get('content'),
                'date_published' : date_part,
            }
            if detail.get('source') != "[Removed]" and detail.get('content'):
                detail_list.append(detail)
        return detail_list
    