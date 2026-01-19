"""
Custom pagination classes for the library API.
"""
from rest_framework.pagination import CursorPagination


class BookCursorPagination(CursorPagination):
    """
    Cursor-based pagination for Books.
    Orders by 'title' for alphabetical sorting.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = 'title'  # Alphabetical by title
    cursor_query_param = 'cursor'


class MemberCursorPagination(CursorPagination):
    """
    Cursor-based pagination for Members.
    Orders by 'name' for alphabetical sorting.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = 'name'  # Alphabetical by name
    cursor_query_param = 'cursor'
