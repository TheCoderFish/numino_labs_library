from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db_helper import Member, DatabaseHelper
from .base_repository import BaseRepository


class MemberRepository(BaseRepository):
    """Repository for Member entity operations"""

    def create_member(self, name: str, email: str) -> Dict[str, Any]:
        """Create a new member"""
        session = self._get_session()
        try:
            member = Member(name=name, email=email)
            session.add(member)
            return DatabaseHelper.sqlalchemy_to_dict(self._commit_and_refresh(session, member))
        except IntegrityError:
            self._rollback_on_error(session, ValueError("Email already exists"))
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def update_member(self, member_id: int, name: str, email: str) -> Optional[Dict[str, Any]]:
        """Update an existing member"""
        session = self._get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            if not member:
                return None
            member.name = name
            member.email = email
            member.updated_at = member.updated_at  # Trigger onupdate
            return DatabaseHelper.sqlalchemy_to_dict(self._commit_and_refresh(session, member))
        except IntegrityError:
            self._rollback_on_error(session, ValueError("Email already exists"))
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get a member by ID"""
        session = self._get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            return DatabaseHelper.sqlalchemy_to_dict(member) if member else None
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def list_members(self) -> List[Dict[str, Any]]:
        """List all members"""
        session = self._get_session()
        try:
            members = session.query(Member).all()
            return [DatabaseHelper.sqlalchemy_to_dict(member) for member in members]
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def list_members_paginated(self, limit: int = 20, cursor: Optional[str] = None,
                             search: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str], bool]:
        """List members with pagination and search"""
        session = self._get_session()
        try:
            query = session.query(Member)

            # Apply search filter
            if search:
                query = query.filter(
                    or_(Member.name.ilike(f"%{search}%"), Member.email.ilike(f"%{search}%"))
                )

            # Apply cursor for pagination
            if cursor:
                try:
                    cursor_id = int(cursor)
                    query = query.filter(Member.id > cursor_id)
                except ValueError:
                    pass  # Invalid cursor, ignore

            # Order by ID for consistent pagination
            query = query.order_by(Member.id)

            # Limit results
            members = query.limit(limit + 1).all()  # +1 to check if there are more

            result = [DatabaseHelper.sqlalchemy_to_dict(member) for member in members[:limit]]

            # Determine next cursor and has_more
            has_more = len(members) > limit
            next_cursor = str(members[limit - 1].id) if result and has_more else None

            return result, next_cursor, has_more
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def search_members(self, query: str) -> List[Dict[str, Any]]:
        """Search members by name or email"""
        session = self._get_session()
        try:
            members = session.query(Member).filter(
                or_(Member.name.ilike(f"%{query}%"), Member.email.ilike(f"%{query}%"))
            ).limit(50).all()
            return [DatabaseHelper.sqlalchemy_to_dict(member) for member in members]
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def member_exists(self, member_id: int) -> bool:
        """Check if a member exists"""
        session = self._get_session()
        try:
            return Member.exists(session, member_id)
        finally:
            session.close()