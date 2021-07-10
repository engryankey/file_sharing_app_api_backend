from django.urls import path
from . import views
from CemBackend.views import MyTokenObtainPairView

urlpatterns = [
    path("register/", views.register_user),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('validateuser/<str:username>/', views.validate_username),
    path('receive_token/<str:token>/', views.receive_token),
]