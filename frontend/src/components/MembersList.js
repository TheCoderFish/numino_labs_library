import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { memberService } from '../services/api';

function MembersList() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentCursor, setCurrentCursor] = useState('');
  const [cursorHistory, setCursorHistory] = useState([]);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);

  useEffect(() => {
    loadMembers(true);
  }, [searchQuery]);

  const loadMembers = async (resetPagination = false, direction = null) => {
    try {
      setLoading(true);

      let cursorToUse = '';
      let updatedHistory = cursorHistory;
      
      if (direction === 'next' && currentCursor) {
        cursorToUse = currentCursor;
      } else if (direction === 'prev' && cursorHistory.length > 0) {
        // For previous, we need to go back to the previous cursor
        updatedHistory = [...cursorHistory];
        cursorToUse = updatedHistory.pop() || '';
        setCursorHistory(updatedHistory);
      } else if (resetPagination) {
        setCurrentCursor('');
        updatedHistory = [];
        setCursorHistory([]);
      }

      const params = {
        limit: 20,
        search: searchQuery
      };

      if (cursorToUse) {
        params.cursor = cursorToUse;
      }

      const response = await memberService.listMembers(params);

      if (direction === 'next') {
        // Save current cursor to history for potential previous navigation
        updatedHistory = [...cursorHistory, currentCursor];
        setCursorHistory(updatedHistory);
      }

      setMembers(response.data.members);
      setCurrentCursor(response.data.next_cursor || '');
      setHasNextPage(response.data.has_more);
      setHasPreviousPage(updatedHistory.length > 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleNextPage = () => {
    if (hasNextPage) {
      loadMembers(false, 'next');
    }
  };

  const handlePreviousPage = () => {
    if (hasPreviousPage) {
      loadMembers(false, 'prev');
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Members</h2>
        <div>
          <Link to="/create-member" className="btn btn-primary me-2">
            Add Member
          </Link>
          <button className="btn btn-outline-secondary" onClick={() => loadMembers(true)}>
            Refresh
          </button>
        </div>
      </div>

      {/* Search Control */}
      <div className="row mb-3">
        <div className="col-md-6">
          <input
            type="text"
            className="form-control"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.length === 0 ? (
                <tr>
                  <td colSpan="4" className="text-center">
                    <div className="alert alert-info mb-0">No members found. Add some members to get started!</div>
                  </td>
                </tr>
              ) : (
                members.map((member) => (
                  <tr key={member.id}>
                    <td>{member.id}</td>
                    <td>{member.name}</td>
                    <td>{member.email}</td>
                    <td>
                      <Link to={`/members/${member.id}/borrowed-books`} className="btn btn-sm btn-outline-primary">
                        View Borrowed Books
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination Controls */}
          {(hasPreviousPage || hasNextPage) && (
            <div className="d-flex justify-content-center mt-3">
              <nav aria-label="Members pagination">
                <ul className="pagination">
                  <li className={`page-item ${!hasPreviousPage ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={handlePreviousPage}
                      disabled={!hasPreviousPage}
                    >
                      Previous
                    </button>
                  </li>
                  <li className={`page-item ${!hasNextPage ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={handleNextPage}
                      disabled={!hasNextPage}
                    >
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MembersList;

