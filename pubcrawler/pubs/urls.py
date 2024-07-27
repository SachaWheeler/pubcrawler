from django.urls import path
from .views import PubPathView

urlpatterns = [
    path('pub-path/', PubPathView.as_view(), name='pub_path'),
]

