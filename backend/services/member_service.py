from typing import List, Optional, Tuple, Dict, Any

from repositories import MemberRepository
from .base_service import BaseService


class MemberService(BaseService):
    """Service for member-related business logic"""

    def __init__(self):
        self._member_repository = MemberRepository()

    def create_member(self, name: str, email: str) -> Dict[str, Any]:
        """Create a new member with validation"""
        self.validate_member_data(name, email)
        return self._member_repository.create_member(name, email)

    def update_member(self, member_id: int, name: str, email: str) -> Optional[Dict[str, Any]]:
        """Update an existing member with validation"""
        self.validate_member_data(name, email)
        return self._member_repository.update_member(member_id, name, email)

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get a member by ID"""
        return self._member_repository.get_member_by_id(member_id)

    def list_members(self) -> List[Dict[str, Any]]:
        """List all members"""
        return self._member_repository.list_members()

    def list_members_paginated(self, limit: int = 20, cursor: Optional[str] = None,
                             search: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str], bool]:
        """List members with pagination and search"""
        return self._member_repository.list_members_paginated(limit, cursor, search)

    def search_members(self, query: str) -> List[Dict[str, Any]]:
        """Search members by name or email"""
        return self._member_repository.search_members(query)

    def member_exists(self, member_id: int) -> bool:
        """Check if a member exists"""
        return self._member_repository.member_exists(member_id)