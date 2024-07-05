from django.shortcuts import render
import requests
import logging
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache
from .models import User, Bookmark
from django.contrib.auth.hashers import make_password, check_password
import re



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create your views here.

class SigninView(TemplateView):
    template_name = 'signin.html'

class SignupView(TemplateView):
    template_name = 'signup.html'


def signup_user(request):
    entered_email = request.POST.get('email')
    entered_password = request.POST.get('new-password')
    con_password = request.POST.get('con-password')
    
    # check if the password matches
    if entered_password != con_password:
        return render(request, 'signup.html', {'error': 'Password doesn\'t match.'})
    
    # find a user with the email address
    users = User.objects.filter(email=entered_email).first()
    
    if users:
        return render(request, 'signup.html', {'error': 'Email already exists.'})
    
    # register the user
    user = User (
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
    
    # save the user id and username in the session
    user = User.objects.get(email=entered_email)
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    
    return redirect('news_api')


def signin_user(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    
    # find the user with email address
    user = User.objects.filter(email=email).first()
    
    if not user:
        return render(request, 'signin.html', {'error': 'Email doesn\'t exist.'})
    
    # check the password
    if not check_password(password, user.password):
        return render(request, 'signin.html', {'error': 'Password is wrong.'})
    
    # save the user id and username in the session
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    
    return redirect('news_api')


def account_setting(request):
    if 'user_id' not in request.session:
        return redirect('news_api')
    
    userid = request.session.get('user_id')
    user = User.objects.get(id=userid)
    
    return render(request, 'account.html', {'user': user})


def change_email(request):
    entered_email = request.POST.get('email')
    
    # check if email is blank
    if entered_email == '':
        return render(request, 'account.html', {'error': 'Please enter an email address.'})
    
    # check if email is valid
    if not valid(entered_email):
        return render(request, 'account.html', {'error': 'Please enter a valid email address.'})
    
    # find a user with the same email
    same_email = User.objects.filter(email=entered_email).first()
    
    if same_email:
        return render(request, 'account.html', {'error': 'Entered email address is used.'})
    
    # find a user with user id and change the email address (and also the username)
    userid = request.session.get('user_id')
    user = User.objects.get(id=userid)

    username = entered_email.split('@')[0]
    user.email = entered_email
    user.username = username
    
    user.save(update_fields=['email', 'username'])
    
    # save the username in the session
    request.session['username'] = username

    return render(request, 'account.html', {'success': 'Email address has been changed.', 'user': user})


def change_password(request):
    old_password = request.POST.get('old-password')
    entered_password = request.POST.get('new-password')
    con_password = request.POST.get('con-password')
    
    # check if password is blank
    if old_password == '' or entered_password == '' or con_password == '':
        return render(request, 'account.html', {'error2': 'Please enter all the password field.'})
    
    userid = request.session.get('user_id')
    user = User.objects.get(id=userid)
    
    # match the password
    if entered_password != con_password:
        return render(request, 'account.html', {'error3': 'Please ensure that password matches.'})
    
    # check the old password
    if not check_password(old_password, user.password):
        return render(request, 'account.html', {'error2': 'Please enter the correct password.'})
    
    # change the password
    user.password = make_password(entered_password)
    user.save(update_fields=['password'])
    
    return render(request, 'account.html', {'success2': 'Password has been changed.', 'user': user})    


def add_to_bookmark(request):
    if 'user_id' not in request.session:
        return render(request, 'signin.html', {'error': 'Please sign in to bookmark.'})
    
    if request.method == 'GET':
        # get the info of the news
        source = request.GET.get('source')
        title = request.GET.get('title')
        date_published = request.GET.get('date')
        country = request.GET.get('country')
        url = request.GET.get('url')
        img_url = request.GET.get('img_url')
        content = request.GET.get('content')
        
        # check if all the field is obtained
        if not all([source, title, date_published, country, url, img_url, content]):
            return JsonResponse({'error': 'Missing parameters.'}, status=400)
        
        # convert the date format
        try:
            date_obj = datetime.strptime(date_published, "%B %d, %Y")
            date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return JsonResponse({'error': 'Invalid date format.'}, status=400)
        
        # find the user with user id
        userid = request.session.get('user_id')
        user = User.objects.get(id=userid)
        
        # check if the bookmark already exist with the user
        bookmarks = Bookmark.objects.filter(user_id=userid, title=title, date_published=date).first()
        
        if bookmarks:
            # delete the bookmark if found
            bookmarks.delete()
            return JsonResponse({'message': 'Deleted'})
        else:
            # add to the bookmark
            bookmark = Bookmark (
                source=source,
                title=title,
                date_published=date,
                country = country,
                url=url,
                image_url=img_url,
                content=content,
                user=user,
            )
            bookmark.save()
            return JsonResponse({'message': title})
    else:
        return JsonResponse({'error': 'Request method is not a GET.'}, status=400)


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
        apikey = "pub_4531191d2b63794a04ccbab7e0be40a2cc9dd"
        request.session.pop('country', None)
        request.session.pop('category', None)
        request.session.pop('language', None)
        url = ('https://newsdata.io/api/1/latest?'
               'category=top&'
               'language=en&'
               f'apikey={apikey}')
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
        apikey = "pub_4531191d2b63794a04ccbab7e0be40a2cc9dd"
        request.session['country'] = country
        category = request.session.get('category', [])
        if not category:
            category='top'
        url = ('https://newsdata.io/api/1/latest?'
               f'country={country}&'
               f'category={category}&'
               f'apikey={apikey}')
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
        apikey = "pub_4531191d2b63794a04ccbab7e0be40a2cc9dd"
        request.session['category'] = category
        country = request.session.get('country', [])
        language = request.session.get('language', [])
        # if not language:
        #     language='en'
        if country:
            url = (
                'https://newsdata.io/api/1/latest?'
                f'country={country}&'
                f'category={category}&'
                f'apikey={apikey}'
            )
        elif not language:
            url = (
                'https://newsdata.io/api/1/latest?'
                f'category={category}&'
                f'apikey={apikey}'
            )
        else:
            url = (
            'https://newsdata.io/api/1/latest?'
            f'category={category}&'
            f'language={language}&'
            f'apikey={apikey}'
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
        apikey = "pub_4531191d2b63794a04ccbab7e0be40a2cc9dd"
        request.session['language'] = language
        category = request.session.get('category', [])
        if not category:
            category='top'
        url = ('https://newsdata.io/api/1/latest?'
               f'category={category}&'
               f'language={language}&'
               f'apikey={apikey}')
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


class BookmarkView(BaseNewsView):
    def get(self, request):
        category = 'bookmark'
        
        status = None
        error = None
        
        articles = {}
        
        if 'user_id' not in request.session:
            status = True
            error = "Sign in to use bookmark feature."
            return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': category})
        
        userid = request.session.get('user_id')
        username = request.session.get('username')
        user = User.objects.get(id=userid)
        
        bookmark_list = Bookmark.objects.filter(user=user)
        news_list = []
        
        for bookmark in bookmark_list:
            detail = {
                'source': bookmark.source,
                'title': bookmark.title,
                'url': bookmark.url,
                'image_url': bookmark.image_url,
                'description': bookmark.content,
                'date_published': bookmark.date_published,
                'country': bookmark.country
            }
            news_list.append(detail)
        
        for i, news in enumerate(news_list, 1):
            articles[i] = news
        
        if not articles:
            status = True
            error = "News Unavailable."
        
        return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': category, 'username': username, 'user_id': userid})


class QueryView(BaseNewsView):
    def get(self, request):
        apikey = "pub_4531191d2b63794a04ccbab7e0be40a2cc9dd"
        query = request.GET.get('query')
        request.session['query'] = query
        url = ('https://newsdata.io/api/1/latest?'
               f'q={query}&'
               f'apikey={apikey}')
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
            return render(request, 'index.html', {'detail': articles, 'status': status, 'error': error,'category': 'query'})
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return Response({'error': 'Failed to fetch data from the API.'}, status=500)


class EndSessionView(BaseNewsView):
    def get(self, request):
    # Flush the session data
        request.session.flush()
        return HttpResponseRedirect('/home')



def valid(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if(re.fullmatch(regex, email)):
        return True

    else:
        return False