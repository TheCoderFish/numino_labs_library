import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { memberService } from '../services/api';

function MembersList() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [nextCursor, setNextCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    loadMembers(true);
  }, [searchQuery]);

  const loadMembers = async (reset = false) => {
    try {
      if (reset) {
        setLoading(true);
        setMembers([]);
        setNextCursor(null);
      } else {
        setLoadingMore(true);
      }
      
      const params = {
        limit: 20,
        search: searchQuery
      };
      
      if (!reset && nextCursor) {
        params.cursor = nextCursor;
      }
      
      const response = await memberService.listMembers(params);
      const newMembers = reset ? response.data.members : [...members, ...response.data.members];
      
      setMembers(newMembers);
      setNextCursor(response.data.next_cursor || null);
      setHasMore(response.data.has_more);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load members');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
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
          
          {hasMore && (
            <div className="text-center mt-3">
              <button
                className="btn btn-outline-primary"
                onClick={() => loadMembers(false)}
                disabled={loadingMore}
              >
                {loadingMore ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MembersList;

