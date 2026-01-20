from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Book, Member, Ledger


class NotEmptyCharField(serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value and not value.strip():
            raise serializers.ValidationError("This field cannot be empty or whitespace only.")
        return value


class MemberSerializer(serializers.ModelSerializer):
    name = NotEmptyCharField(max_length=255)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        qs = Member.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class BookSerializer(serializers.ModelSerializer):
    title = NotEmptyCharField(max_length=255)
    author = NotEmptyCharField(max_length=255)
    current_member_name = serializers.CharField(source='current_member.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'is_borrowed', 'current_member', 'current_member_name', 'created_at',
                  'updated_at']
        read_only_fields = ['id', 'is_borrowed', 'current_member', 'current_member_name', 'created_at', 'updated_at']


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['id', 'book', 'member', 'action_type', 'log_date', 'due_date_snapshot']
        read_only_fields = ['id', 'log_date', 'due_date_snapshot']


class BorrowBookSerializer(serializers.Serializer):
    member_id = serializers.IntegerField(required=True)

    def validate_member_id(self, value):
        if not Member.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Member with id {value} not found.")
        return value

    def validate(self, attrs):
        # We need the book instance from context
        book = self.context.get('book')
        if not book:
            raise serializers.ValidationError("Book context is required.")
        
        if book.is_borrowed:
            raise serializers.ValidationError("Book is already borrowed.")
            
        return attrs

    def save(self, **kwargs):
        member_id = self.validated_data['member_id']
        book = self.context['book']
        
        with transaction.atomic():
            # Refresh book with lock
            book = Book.objects.select_for_update().get(id=book.id)
            if book.is_borrowed:
                # Double check inside lock
                raise serializers.ValidationError("Book is already borrowed.")
            
            member = Member.objects.get(id=member_id)
            
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


class ReturnBookSerializer(serializers.Serializer):
    member_id = serializers.IntegerField(required=True)

    def validate_member_id(self, value):
        if not Member.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Member with id {value} not found.")
        return value

    def validate(self, attrs):
        book = self.context.get('book')
        member_id = attrs.get('member_id')
        
        if not book:
            raise serializers.ValidationError("Book context is required.")
            
        if not book.is_borrowed:
            raise serializers.ValidationError("Book is not currently borrowed.")
            
        if book.current_member_id != member_id:
            raise serializers.ValidationError("Book is not borrowed by this member.")
            
        return attrs

    def save(self, **kwargs):
        member_id = self.validated_data['member_id']
        book = self.context['book']
        
        with transaction.atomic():
            book = Book.objects.select_for_update().get(id=book.id)
            if not book.is_borrowed:
                raise serializers.ValidationError("Book is not currently borrowed.")
            
            member = Member.objects.get(id=member_id)
            
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
