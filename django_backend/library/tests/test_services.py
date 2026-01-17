import pytest
from library.models import Member, Book, Ledger
from library import services
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_create_member():
    member = services.create_member(name="John Doe", email="john@example.com")
    assert member.name == "John Doe"
    assert member.email == "john@example.com"
    assert Member.objects.count() == 1

@pytest.mark.django_db
def test_create_member_duplicate_email():
    services.create_member(name="John Doe", email="john@example.com")
    with pytest.raises(ValidationError):
        services.create_member(name="Jane Doe", email="john@example.com")

@pytest.mark.django_db
def test_create_book():
    book = services.create_book(title="The Hobbit", author="J.R.R. Tolkien")
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert Book.objects.count() == 1
    assert not book.is_borrowed

@pytest.mark.django_db
def test_borrow_book_success(member, book):
    ledger = services.borrow_book(book_id=book.id, member_id=member.id)
    
    book.refresh_from_db()
    assert book.is_borrowed
    assert book.current_member == member
    
    assert ledger.action_type == Ledger.ActionType.BORROW
    assert ledger.book == book
    assert ledger.member == member

@pytest.mark.django_db
def test_borrow_book_already_borrowed(member, book):
    services.borrow_book(book_id=book.id, member_id=member.id)
    
    # Try borrowing same book again by same user
    with pytest.raises(ValueError, match="Book is already borrowed"):
         services.borrow_book(book_id=book.id, member_id=member.id)

    # Try borrowing same book by another user
    other_member = services.create_member("Jane", "jane@example.com")
    with pytest.raises(ValueError, match="Book is already borrowed"):
         services.borrow_book(book_id=book.id, member_id=other_member.id)

@pytest.mark.django_db
def test_return_book_success(member, book):
    # Setup: borrow first
    services.borrow_book(book_id=book.id, member_id=member.id)
    
    # Return
    ledger = services.return_book(book_id=book.id, member_id=member.id)
    
    book.refresh_from_db()
    assert not book.is_borrowed
    assert book.current_member is None
    
    assert ledger.action_type == Ledger.ActionType.RETURN

@pytest.mark.django_db
def test_return_book_not_borrowed(member, book):
    with pytest.raises(ValueError, match="Book is not currently borrowed"):
        services.return_book(book_id=book.id, member_id=member.id)

@pytest.mark.django_db
def test_return_book_wrong_member(member, book):
    services.borrow_book(book_id=book.id, member_id=member.id)
    other_member = services.create_member("Jane", "jane@example.com")
    
    with pytest.raises(ValueError, match="Book is not borrowed by this member"):
        services.return_book(book_id=book.id, member_id=other_member.id)
