# system/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, BookViewSet, CategoryViewSet, BorrowView, ReturnView, UserPenaltyView

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('borrow/', BorrowView.as_view(), name='borrow'),
    path('return/', ReturnView.as_view(), name='return'),
    path('users/<int:id>/penalties/', UserPenaltyView.as_view(), name='user-penalties'),
]