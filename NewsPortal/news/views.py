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

class BaseNewsView(APIView):
    def getDetails(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        articles = data.get('results', [])
        if not articles:
            logger.info("No articles found.")
            return Response({'error': 'No articles found.'}, status=404)
        detail_list = []
        for item in articles:
            if not isinstance(item, dict):
                logger.warning(f"Unexpected item type: {type(item)}, value: {item}")
                continue
            date_published = item.get('pubDate')
            date_part = ""
            if date_published:
                try:
                    datetime_obj = datetime.strptime(date_published, '%Y-%m-%d %H:%M:%S')
                    date_part = datetime_obj.date()
                except ValueError:
                    logger.error(f"Date parsing error for {date_published}")
            detail = {
                'source': item.get('source_id'),
                'title': item.get('title'),
                'url': item.get('source_url'),
                'image_url': item.get('image_url'),
                'description': item.get('description'),
                'date_published': date_part,
            }
            if detail.get('source') and detail.get('description'):
                detail_list.append(detail)
        return detail_list

class NewsportalView(BaseNewsView):
    def get(self, request):
        url = ('https://newsdata.io/api/1/latest?'
               'category=top&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            detail = self.getDetails(url)
            return Response(detail)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)

    
class SetCountryView(BaseNewsView):
    def get(self, request, country):
        url = ('https://newsdata.io/api/1/latest?'
               f'country={country}&'
               f'category=top&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            detail = self.getDetails(url)
            return Response(detail)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)
    
    
class SetCategoryView(BaseNewsView):
    def get(self, request, country, category):
        url = ('https://newsdata.io/api/1/latest?'
               f'country={country}&'
               f'category={category}&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            detail = self.getDetails(url)
            return Response(detail)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)
        
class SetLanguageView(BaseNewsView):
    def get(self, request, country, category, language):
        url = ('https://newsdata.io/api/1/latest?'
               f'country={country}&'
               f'category={category}&'
               f'language={language}&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            detail = self.getDetails(url)
            return Response(detail)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)