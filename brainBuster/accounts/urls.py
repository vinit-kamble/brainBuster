from django.urls import path
from .views import CustomLoginView, signup_view, logout_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
]