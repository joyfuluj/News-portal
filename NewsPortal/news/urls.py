from django.urls import path
# from . import views
from .views import IndexView, SigninView, SignupView, AccountView, NewsportalView, SetCountryView, SetCategoryView, SetLanguageView, FilteredNewsView, FilterView, EndSessionView

# urlpatterns = [
#     path('', views.index, name="index"),
# ]

urlpatterns = [
    path('', IndexView.as_view()),
    path('signin', SigninView.as_view()),
    path('signup', SignupView.as_view()),
    path('account', AccountView.as_view()),
    # path('end/home/', NewsportalView.as_view(), name='news_api'),
    path('home', NewsportalView.as_view(), name='news_api'),
    path('home/country/<str:country>/', SetCountryView.as_view(), name='country_api'),
    path('home/category/<str:category>', SetCategoryView.as_view(), name='category_api'),
    path('home/language/<str:language>', SetLanguageView.as_view(), name='lang_api'),
    path('filtered-news/', FilteredNewsView.as_view(), name='news_view'),
    path('home/filter/<str:country>/<str:category>/<str:language>', FilterView.as_view(), name='filter_api'),
    path('end/', EndSessionView.as_view(), name='end_view'),
]