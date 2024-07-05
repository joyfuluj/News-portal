from django.urls import path
from . import views
from .views import SigninView, SignupView, NewsportalView, SetCountryView, SetCategoryView, SetLanguageView, BookmarkView, EndSessionView, QueryView

urlpatterns = [
    path('', NewsportalView.as_view(), name='news_api'),
    path('signin', SigninView.as_view()),
    path('signup', SignupView.as_view()),
    path('home', NewsportalView.as_view(), name='news_api'),
    path('home/country/<str:country>/', SetCountryView.as_view(), name='country_api'),
    path('home/category/<str:category>', SetCategoryView.as_view(), name='category_api'),
    path('home/language/<str:language>', SetLanguageView.as_view(), name='lang_api'),
    path('home/bookmark', BookmarkView.as_view()),
    path('home/query', QueryView.as_view(), name='query_api'),
    path('end/', EndSessionView.as_view(), name='end_view'),
    path('signin-user', views.signin_user),
    path('signup-user', views.signup_user),
    path('account-setting', views.account_setting),
    path('change-email', views.change_email),
    path('change-pass', views.change_password),
    path('add-to-bookmark', views.add_to_bookmark, name='bookmark'),
]