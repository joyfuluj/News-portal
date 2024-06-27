from django.shortcuts import render
import json
import requests
import logging
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.cache import cache
from .models import User, Bookmark
from django.contrib.auth.hashers import check_password



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create your views here.

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

def signup_user(request):
    entered_email = request.POST.get('email')
    entered_password = request.POST.get('new-password')
    con_password = request.POST.get('con-password')
    
    if entered_password != con_password:
        return render(request, 'signup.html', {'error': 'Password doesn\'t match.'})
    
    users = User.objects.filter(email=entered_email).first()
    
    if users:
        return render(request, 'signup.html', {'error': 'Email already exists.'})
    
    user = User(
        username=entered_email.split('@')[0],
        email=entered_email,
        password=entered_password,
    )
    # user = User(
    #     username=joyful,
    #     email=joyful@yahoo.co.jp,
    #     password='joyful123',
    # )
    
    user.save()
    
    user = User.objects.get(email=entered_email)
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    
    return redirect('news_api')


def signin_user(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = User.objects.get(email=email)
    
    if user:
        if check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('news_api')
        else:
            return render(request, 'signin.html', {'error': 'Password is wrong.'})
    else:
        return render(request, 'signin.html', {'error': 'Email doesn\'t exist.'})


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
        cache_key = f"news_{url}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        articles = data.get('results', [])
        if not articles:
            logger.info("No articles found.")
            return []

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
            country = ', '.join([country for country in item.get('country') if country])
            country = ' '.join(word.capitalize() for word in country.split(' '))
            detail = {
                'source': item.get('source_id'),
                'title': item.get('title'),
                'url': item.get('source_url'),
                'image_url': item.get('image_url'),
                'description': item.get('description'),
                'date_published': date_part,
                'country': country
            }
            if detail.get('source') and detail.get('description'):
                detail_list.append(detail)
        # Cache the result for 1 hour
        cache.set(cache_key, detail_list, timeout=3600)
        return detail_list

class NewsportalView(BaseNewsView):
    template_name = 'index.html'
    def get(self, request):
        url = ('https://newsdata.io/api/1/latest?'
               'category=top&'
               'language=en&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            detail = self.getDetails(url) #list of dictionary
            articles = {}
            for i, news in enumerate(detail, 1):
                articles[i] = news
            # return Response(detail)
            username = request.session.get('username')
            userid = request.session.get('user_id')
            return render(request, 'index.html', {'detail': articles, 'category': 'top', 'username': username, 'user_id': userid})
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)

    
class SetCountryView(BaseNewsView):
    def get(self, request, country):
        request.session['country'] = country
        category = request.session.get('category', [])
        language = request.session.get('language', [])
        if not category:
            category='top'
        if not language:
            language='en'
        url = ('https://newsdata.io/api/1/latest?'
               f'country={country}&'
               f'category={category}&'
               f'language={language}&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            status = None
            error = None
            detail = self.getDetails(url) #list of dictionary
            articles = {}
            for i, news in enumerate(detail, 1):
                articles[i] = news
            if not articles:
                status = True
                error = "News Unavailable."
            # return Response(detail)
            username = request.session.get('username')
            userid = request.session.get('user_id')
            return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': category, 'country': country, 'username': username, 'user_id': userid})
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)


class SetCategoryView(BaseNewsView):
    def get(self, request, category):
        request.session['category'] = category
        country = request.session.get('country', [])
        language = request.session.get('language', [])
        if not country:
            country='us'
        if not language:
            language='en'
        url = (
            'https://newsdata.io/api/1/latest?'
            f'country={country}&'
            f'category={category}&'
            f'language={language}&'
            'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd'
        )
        try:
            status = None
            error = None
            detail = self.getDetails(url) #list of dictionary
            articles = {}
            for i, news in enumerate(detail, 1):
                articles[i] = news
            if not articles:
                status = True
                error = "News Unavailable."
            # return Response(detail)
            username = request.session.get('username')
            userid = request.session.get('user_id')
            return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': category, 'username': username, 'user_id': userid})
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)


class SetLanguageView(BaseNewsView):
    def get(self, request, language):
        request.session['language'] = language
        category = request.session.get('category', [])
        if not category:
            category='top'
        url = ('https://newsdata.io/api/1/latest?'
               f'category={category}&'
               f'language={language}&'
               'apikey=pub_4531191d2b63794a04ccbab7e0be40a2cc9dd')
        try:
            status = None
            error = None
            detail = self.getDetails(url) #list of dictionary
            articles = {}
            for i, news in enumerate(detail, 1):
                articles[i] = news
            if not articles:
                status = True
                error = "News Unavailable."
            # return Response(detail)
            username = request.session.get('username')
            userid = request.session.get('user_id')
            return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': category, 'username': username, 'user_id': userid})
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)


class EndSessionView(BaseNewsView):
    def get(self, request):
    # Flush the session data
        request.session.flush()
        return HttpResponseRedirect('/home')


class FilterView(BaseNewsView):
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


class FilteredNewsView(BaseNewsView):
    def get(self, request):
        countries = request.GET.getlist('country')
        categories = request.GET.getlist('category')
        languages = request.GET.getlist('language')
        
        if not countries or not categories or not languages:
            # Handle the case where no checkboxes are selected
            return redirect('home')  # Adjust as needed
        
        countries_param = ','.join(countries)
        categories_param = ','.join(categories)
        languages_param = ','.join(languages)
        
        url = reverse('filter_api', kwargs={
            'country': countries_param,
            'category': categories_param,
            'language': languages_param,
        })
        
        return redirect(url)