import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';

function DataTable({
  title,
  columns,
  actions,
  loadData,
  searchPlaceholder = 'Search...',
  hasFilter = false,
  filterOptions = [],
  initialFilter = 'all',
  addButton = null,
  refreshButton = true,
  refreshTrigger = 0
}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState(initialFilter);
  const [currentCursor, setCurrentCursor] = useState('');
  const [cursorHistory, setCursorHistory] = useState([]);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);

  const loadTableData = async (resetPagination = false, direction = null) => {
    try {
      setLoading(true);

      let cursorToUse = '';
      if (direction === 'next' && currentCursor) {
        cursorToUse = currentCursor;
      } else if (direction === 'prev' && cursorHistory.length > 0) {
        // For previous, we need to go back to the previous cursor
        const newHistory = [...cursorHistory];
        cursorToUse = newHistory.pop() || '';
        setCursorHistory(newHistory);
      } else if (resetPagination) {
        setCurrentCursor('');
        setCursorHistory([]);
      }

      const params = {
        page_size: 20,
        search: searchQuery
      };

      if (hasFilter) {
        params.filter = filter;
      }

      if (cursorToUse) {
        params.cursor = cursorToUse;
      }

      const response = await loadData(params);

      if (direction === 'next') {
        // Save current cursor to history for potential previous navigation
        setCursorHistory(prev => [...prev, currentCursor]);
      }

      setData(response.data);
      setCurrentCursor(response.next_cursor || '');
      setHasNextPage(response.has_more);
      setHasPreviousPage(cursorHistory.length > 0 || (direction === 'next'));
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to load data';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTableData(true);
  }, [searchQuery, filter, refreshTrigger]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };

  const handleNextPage = () => {
    if (hasNextPage) {
      loadTableData(false, 'next');
    }
  };

  const handlePreviousPage = () => {
    if (hasPreviousPage) {
      loadTableData(false, 'prev');
    }
  };

  const handleRefresh = () => {
    loadTableData(true);
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{title}</h2>
        <div>
          {addButton && (
            <Link to={addButton.to} className="btn btn-primary me-2">
              {addButton.text}
            </Link>
          )}
          {refreshButton && (
            <button className="btn btn-outline-secondary" onClick={handleRefresh}>
              Refresh
            </button>
          )}
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="row mb-3">
        <div className="col-md-6">
          <input
            type="text"
            className="form-control"
            placeholder={searchPlaceholder}
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
        {hasFilter && (
          <div className="col-md-3">
            <select
              className="form-select"
              value={filter}
              onChange={handleFilterChange}
            >
              {filterOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}
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
                {columns.map(column => (
                  <th key={column.key}>{column.label}</th>
                ))}
                {actions && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {data.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + (actions ? 1 : 0)} className="text-center">
                    <div className="alert alert-info mb-0">No data found.</div>
                  </td>
                </tr>
              ) : (
                data.map((item, index) => (
                  <tr key={item.id || index}>
                    {columns.map(column => (
                      <td key={column.key}>
                        {column.render ? column.render(item) : item[column.key]}
                      </td>
                    ))}
                    {actions && (
                      <td>
                        <div className="d-flex gap-2">
                          {actions(item)}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination Controls */}
          {(hasPreviousPage || hasNextPage) && (
            <div className="d-flex justify-content-center mt-3">
              <nav aria-label={`${title} pagination`}>
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

export default DataTable;