from django.urls import path
# from . import views
from .views import IndexView, SigninView, SignupView, AccountView

# urlpatterns = [
#     path('', views.index, name="index"),
# ]

urlpatterns = [
    path('', IndexView.as_view()),
    path('signin', SigninView.as_view()),
    path('signup', SignupView.as_view()),
    path('account', AccountView.as_view()),
]