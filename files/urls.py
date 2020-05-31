from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('', FileUploadView.as_view()),
    path('/list', FileUploadView.as_view()),
    path('/<fname>', FileDeleteRet.as_view())

]
