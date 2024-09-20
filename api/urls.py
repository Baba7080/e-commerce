from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import *


urlpatterns = [

    path('api/v1/register', RegisterView.as_view(), name='register'),
    path('api/v1/login', LoginView.as_view(), name='login'),

    path('api/v1/products/', ProductDetailsView.as_view(), name='product-list-create'),

    path('api/v1/products/category/<int:category_id>/', ProductListView.as_view(), name='product-list-by-category'),



]