from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Book, Member, Ledger


def create_member(name: str, email: str) -> Member:
    if Member.objects.filter(email=email).exists():
        raise ValidationError(f"Email {email} already exists.")
    return Member.objects.create(name=name, email=email)


def create_book(title: str, author: str) -> Book:
    return Book.objects.create(title=title, author=author)


def borrow_book(book_id: int, member_id: int) -> Ledger:
    with transaction.atomic():
        # Lock the book row
        try:
            book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            raise ValueError(f"Book with id {book_id} not found.")

        # Check member
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            raise ValueError(f"Member with id {member_id} not found.")

        if book.is_borrowed:
            raise ValueError("Book is already borrowed.")

        book.is_borrowed = True
        book.current_member = member
        book.save()

        ledger = Ledger.objects.create(
            book=book,
            member=member,
            action_type=Ledger.ActionType.BORROW,
            log_date=timezone.now()
        )
        return ledger


def return_book(book_id: int, member_id: int) -> Ledger:
    with transaction.atomic():
        try:
            book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            raise ValueError(f"Book with id {book_id} not found.")

        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            raise ValueError(f"Member with id {member_id} not found.")

        if not book.is_borrowed:
            raise ValueError("Book is not currently borrowed.")

        if book.current_member_id != member_id:
            raise ValueError("Book is not borrowed by this member.")

        book.is_borrowed = False
        book.current_member = None
        book.updated_at = timezone.now()
        book.save()

        ledger = Ledger.objects.create(
            book=book,
            member=member,
            action_type=Ledger.ActionType.RETURN,
            log_date=timezone.now()
        )
        return ledger
