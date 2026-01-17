from rest_framework import serializers
from .models import Book, Member, Ledger


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        # We can also rely on model unique constraint, but explicit check is nice.
        # However, for updates, we need to exclude self.
        qs = Member.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class BookSerializer(serializers.ModelSerializer):
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
