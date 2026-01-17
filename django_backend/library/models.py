from django.db import models
from django.utils import timezone


class Member(models.Model):
    name = models.TextField()
    email = models.TextField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'member'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.TextField()
    author = models.TextField()
    is_borrowed = models.BooleanField(default=False)
    current_member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_books',
        db_column='current_member_id'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'book'
        indexes = [
            models.Index(fields=['is_borrowed'], name='idx_book_is_borrowed'),
            models.Index(fields=['current_member'], name='idx_book_current_member'),
        ]

    def __str__(self):
        return self.title


class Ledger(models.Model):
    class ActionType(models.TextChoices):
        BORROW = 'BORROW', 'Borrow'
        RETURN = 'RETURN', 'Return'

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    action_type = models.TextField(choices=ActionType.choices)
    log_date = models.DateTimeField(default=timezone.now)
    due_date_snapshot = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ledger'
        indexes = [
            models.Index(fields=['book'], name='idx_ledger_book_id'),
            models.Index(fields=['member'], name='idx_ledger_member_id'),
            models.Index(fields=['action_type'], name='idx_ledger_action_type'),
        ]
