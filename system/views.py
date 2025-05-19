# system/views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import F

from .models import CustomUser, Category, Book, Borrow
from .serializers import UserRegistrationSerializer, CategorySerializer, BookSerializer, BorrowSerializer

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Book.objects.all()
        category = self.request.query_params.get('category', None)
        author = self.request.query_params.get('author', None)
        
        if category:
            queryset = queryset.filter(category__name=category)
        if author:
            queryset = queryset.filter(author__icontains=author)
        
        return queryset

class BorrowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'error': 'book_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Check borrowing limit
        active_borrows = Borrow.objects.filter(
            user=request.user, 
            return_date__isnull=True
        ).count()
        
        if active_borrows >= 3:
            return Response({'error': 'Borrowing limit reached'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                book = Book.objects.select_for_update().get(id=book_id)
                
                if book.available_copies <= 0:
                    return Response({'error': 'No copies available'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                due_date = timezone.now().date() + timedelta(days=14)
                borrow = Borrow.objects.create(
                    user=request.user,
                    book=book,
                    due_date=due_date
                )
                
                book.available_copies = F('available_copies') - 1
                book.save()

                serializer = BorrowSerializer(borrow)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        borrows = Borrow.objects.filter(
            user=request.user,
            return_date__isnull=True
        )
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)

class ReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        borrow_id = request.data.get('borrow_id')
        if not borrow_id:
            return Response({'error': 'borrow_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                borrow = Borrow.objects.select_related('book').get(
                    id=borrow_id,
                    user=request.user,
                    return_date__isnull=True
                )

                return_date = timezone.now().date()
                days_late = max((return_date - borrow.due_date).days, 0)

                borrow.return_date = return_date
                borrow.save()

                borrow.book.available_copies = F('available_copies') + 1
                borrow.book.save()

                if days_late > 0:
                    request.user.penalty_points = F('penalty_points') + days_late
                    request.user.save()

                return Response({
                    'message': 'Book returned successfully',
                    'days_late': days_late
                })

        except Borrow.DoesNotExist:
            return Response({'error': 'Borrow record not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class UserPenaltyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        # Admins can view any user's penalties, users can view their own
        if request.user.is_staff or request.user.id == id:
            try:
                user = CustomUser.objects.get(id=id)
                return Response({'user_id': user.id, 'penalty_points': user.penalty_points})
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        return Response({'error': 'Forbidden'}, status=403)