import pytest
from server import LibraryService
import member_pb2
import grpc

class MockContext:
    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

class TestMembers:
    def test_create_member_success(self, clean_database):
        """Test creating a member successfully"""
        service = LibraryService()
        request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        context = MockContext()

        response = service.CreateMember(request, context)

        assert response.message == "Member created successfully"
        assert response.member.name == "John Doe"
        assert response.member.email == "john@example.com"

    def test_create_member_duplicate_email(self, clean_database):
        """Test creating a member with duplicate email"""
        service = LibraryService()

        # Create first member
        request1 = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        context1 = MockContext()
        service.CreateMember(request1, context1)

        # Try to create second member with same email
        request2 = member_pb2.CreateMemberRequest(name="Jane Doe", email="john@example.com")
        context2 = MockContext()
        response2 = service.CreateMember(request2, context2)

        assert context2.code == grpc.StatusCode.ALREADY_EXISTS

    def test_update_member_success(self, clean_database):
        """Test updating a member successfully"""
        service = LibraryService()

        # Create a member first
        create_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        create_context = MockContext()
        create_response = service.CreateMember(create_request, create_context)
        member_id = create_response.member.id

        # Update the member
        update_request = member_pb2.UpdateMemberRequest(id=member_id, name="John Smith", email="johnsmith@example.com")
        update_context = MockContext()
        update_response = service.UpdateMember(update_request, update_context)

        assert update_response.message == "Member updated successfully"
        assert update_response.member.name == "John Smith"
        assert update_response.member.email == "johnsmith@example.com"

    def test_update_member_not_found(self, clean_database):
        """Test updating a non-existent member"""
        service = LibraryService()
        request = member_pb2.UpdateMemberRequest(id=999, name="Test", email="test@example.com")
        context = MockContext()

        response = service.UpdateMember(request, context)

        assert context.code == grpc.StatusCode.NOT_FOUND

    def test_update_member_duplicate_email(self, clean_database):
        """Test updating a member to an existing email"""
        service = LibraryService()

        # Create two members
        request1 = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        context1 = MockContext()
        response1 = service.CreateMember(request1, context1)

        request2 = member_pb2.CreateMemberRequest(name="Jane Doe", email="jane@example.com")
        context2 = MockContext()
        response2 = service.CreateMember(request2, context2)

        # Try to update second member to first member's email
        update_request = member_pb2.UpdateMemberRequest(id=response2.member.id, name="Jane Doe", email="john@example.com")
        update_context = MockContext()
        update_response = service.UpdateMember(update_request, update_context)

        assert update_context.code == grpc.StatusCode.ALREADY_EXISTS

    def test_list_members(self, clean_database):
        """Test listing members"""
        service = LibraryService()

        # Create some members
        members_data = [
            ("John Doe", "john@example.com"),
            ("Jane Smith", "jane@example.com"),
        ]

        for name, email in members_data:
            request = member_pb2.CreateMemberRequest(name=name, email=email)
            context = MockContext()
            service.CreateMember(request, context)

        # List members
        list_request = member_pb2.ListMembersRequest()
        list_context = MockContext()
        list_response = service.ListMembers(list_request, list_context)

        assert len(list_response.members) == 2
        names = [member.name for member in list_response.members]
        assert "John Doe" in names
        assert "Jane Smith" in names

    def test_search_members(self, clean_database):
        """Test searching members"""
        service = LibraryService()

        # Create some members
        members_data = [
            ("John Doe", "john@example.com"),
            ("Jane Smith", "jane@example.com"),
            ("Bob Johnson", "bob@example.com"),
        ]

        for name, email in members_data:
            request = member_pb2.CreateMemberRequest(name=name, email=email)
            context = MockContext()
            service.CreateMember(request, context)

        # Search for "John"
        search_request = member_pb2.SearchMembersRequest(query="John")
        search_context = MockContext()
        search_response = service.SearchMembers(search_request, search_context)

        assert len(search_response.members) == 2
        names = [member.name for member in search_response.members]
        assert "John Doe" in names
        assert "Bob Johnson" in names  # "Johnson" contains "John"