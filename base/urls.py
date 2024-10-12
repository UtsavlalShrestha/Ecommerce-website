from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('signup/', views.signupUser, name="signup"),
    path('view_cart/', views.view_cart, name="view_cart"),
    path('remove_cart/<int:id>', views.remove_cart, name="remove_cart"),
    path('add_to_cart/<int:product_id>', views.add_to_cart, name="add_to_cart"),
    # path('cart/<int:id>', views.cart, name="cart"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('checkout/', views.checkout, name="checkout"),


]