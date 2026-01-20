from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import Book, Member
from .serializers import (
    BookSerializer, MemberSerializer, LedgerSerializer,
    BorrowBookSerializer, ReturnBookSerializer
)
from .pagination import BookCursorPagination, MemberCursorPagination
from . import selectors


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.none()  # Placeholder, overridden by get_queryset
    serializer_class = BookSerializer
    pagination_class = BookCursorPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author']
    ordering_fields = ['id', 'title', 'updated_at']
    ordering = ['title']  # Match pagination ordering

    def get_queryset(self):
        queryset = selectors.get_book_list()
        
        # Handle filter parameter for availability
        filter_param = self.request.query_params.get('filter', None)
        if filter_param == 'available':
            queryset = queryset.filter(is_borrowed=False)
        elif filter_param == 'borrowed':
            queryset = queryset.filter(is_borrowed=True)
        
        # Handle is_borrowed parameter (for BorrowBook component)
        is_borrowed_param = self.request.query_params.get('is_borrowed', None)
        if is_borrowed_param is not None:
            # Convert string to boolean
            is_borrowed = is_borrowed_param.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_borrowed=is_borrowed)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'borrow':
            return BorrowBookSerializer
        if self.action == 'return_book':
            return ReturnBookSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'book': book})
        serializer.is_valid(raise_exception=True)
        ledger = serializer.save()
        return Response(LedgerSerializer(ledger).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'book': book})
        serializer.is_valid(raise_exception=True)
        ledger = serializer.save()
        return Response(LedgerSerializer(ledger).data, status=status.HTTP_200_OK)


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.none()
    serializer_class = MemberSerializer
    pagination_class = MemberCursorPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'email']

    def get_queryset(self):
        return selectors.get_member_list()

    @action(detail=True, methods=['get'], url_path='borrowed-books')
    def borrowed_books(self, request, pk=None):
        # We can implement a selector for this
        books = Book.objects.filter(current_member_id=pk)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='check-email')
    def check_email(self, request):
        email = request.query_params.get('email', '').strip()
        if not email:
            return Response({'available': False, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email is valid format first (optional, but good)
        # We can just check existence
        exists = Member.objects.filter(email=email).exists()
        return Response({'available': not exists})
