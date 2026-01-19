from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import Book, Member
from .serializers import BookSerializer, MemberSerializer, LedgerSerializer
from .pagination import BookCursorPagination, MemberCursorPagination
from . import services, selectors


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

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        member_id = request.data.get('member_id')
        if not member_id:
            return Response({"error": "member_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ledger = services.borrow_book(book_id=pk, member_id=member_id)
            return Response(LedgerSerializer(ledger).data, status=status.HTTP_200_OK)
        except ValueError as e:
            # Business logic errors (not found, already borrowed)
            if "not found" in str(e).lower():
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        member_id = request.data.get('member_id')
        if not member_id:
            return Response({"error": "member_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ledger = services.return_book(book_id=pk, member_id=member_id)
            return Response(LedgerSerializer(ledger).data, status=status.HTTP_200_OK)
        except ValueError as e:
            if "not found" in str(e).lower():
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
