import React from 'react';
import { Link } from 'react-router-dom';
import { memberService } from '../services/api';
import DataTable from './DataTable';

function MembersList() {
  const loadMembers = async (params) => {
    // API service already returns {data, next_cursor, has_more}
    return await memberService.listMembers(params);
  };

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' }
  ];

  const actions = (member) => (
    <>
      <Link
        to={`/members/${member.id}/edit`}
        state={{ member }}
        className="btn btn-sm btn-outline-secondary"
      >
        Edit
      </Link>
      <Link to={`/members/${member.id}/borrowed-books`} className="btn btn-sm btn-outline-primary">
        View Borrowed Books
      </Link>
    </>
  );

  return (
    <DataTable
      title="Members"
      columns={columns}
      actions={actions}
      loadData={loadMembers}
      searchPlaceholder="Search by name or email..."
      hasFilter={false}
      addButton={{ text: 'Add Member', to: '/create-member' }}
    />
  );
}

export default MembersList;

