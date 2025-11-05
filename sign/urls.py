from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView, make_author, AccountView, UpdateProfile

urlpatterns = [
    path('login/', LoginView.as_view(template_name = 'sign/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name = 'sign/logout.html'), name='logout'),
    path('signup/', BaseRegisterView.as_view(template_name = 'sign/signup.html'), name='signup'),
    path('author/', make_author, name='author'),
    path('account/', AccountView.as_view(), name = 'account'),
    path('edit/', UpdateProfile.as_view(template_name = 'sign/update_profile.html'), name='user_update'),
]