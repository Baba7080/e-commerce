from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import *


urlpatterns = [

    path('api/v1/register', RegisterView.as_view(), name='register'),
    path('api/v1/login', LoginView.as_view(), name='login'),

    path('api/v1/products/list', ProductDetailsView.as_view(), name='product-list-create'),
    path('api/v1/products/list/<int:pk>', ProductDetailsView.as_view(), name='product-list-create'),

    path('api/v1/products/category/<int:category_id>/', ProductListView.as_view(), name='product-list-by-category'),

    path('api/v1/products/<int:product_id>', ProductDetailView.as_view(), name='product-details-by-category'),

    #Cart
    path('api/v1/cart/management', CartManagementView.as_view(), name='create-order'),
    path('api/v1/cart/increase/<int:product_id>', IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('api/v1/cart/decrease/<int:product_id>', DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('api/v1/cart/remove/<int:product_id>', RemoveCartProductView.as_view(), name='remove-product'),







]