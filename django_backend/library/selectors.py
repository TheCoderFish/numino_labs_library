from django.db.models import QuerySet
from .models import Book, Member

def get_book_list(*, filters=None) -> QuerySet[Book]:
    filters = filters or {}
    qs = Book.objects.select_related('current_member').all()
    # Apply filters if needed, largely handled by DRF filter backends usually, 
    # but we can enforce basics here or return base QS.
    return qs.order_by('id')

def get_member_list() -> QuerySet[Member]:
    return Member.objects.all().order_by('id')
