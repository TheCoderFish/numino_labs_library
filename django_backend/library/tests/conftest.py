import pytest
import factory
from factory.django import DjangoModelFactory
from library.models import Book, Member, Ledger

class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    name = factory.Faker('name')
    email = factory.Faker('email')

class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker('sentence', nb_words=4)
    author = factory.Faker('name')

@pytest.fixture
def member():
    return MemberFactory()

@pytest.fixture
def book():
    return BookFactory()
