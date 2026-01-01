import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ErrorBoundary from './components/ErrorBoundary';
import Dashboard from './components/Dashboard';
import BooksList from './components/BooksList';
import MembersList from './components/MembersList';
import CreateBook from './components/CreateBook';
import CreateMember from './components/CreateMember';
import BorrowBook from './components/BorrowBook';
import MemberBorrowedBooks from './components/MemberBorrowedBooks';

function App() {
  return (
    <ErrorBoundary>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="App">
          <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
            <div className="container">
              <Link className="navbar-brand" to="/">
                📚 Library Service
              </Link>
              <button
                className="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
                aria-controls="navbarNav"
                aria-expanded="false"
                aria-label="Toggle navigation"
              >
                <span className="navbar-toggler-icon"></span>
              </button>
              <div className="collapse navbar-collapse" id="navbarNav">
                <ul className="navbar-nav ms-auto">
                  <li className="nav-item">
                    <Link className="nav-link" to="/">
                      Recent Updates
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/books">
                      Books
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/members">
                      Members
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/borrow-book">
                      Borrow Book
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </nav>

          <div className="container mt-4">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/books" element={<BooksList />} />
              <Route path="/books/:id/edit" element={<CreateBook />} />
              <Route path="/members" element={<MembersList />} />
              <Route path="/members/:id/edit" element={<CreateMember />} />
              <Route path="/members/:id/borrowed-books" element={<MemberBorrowedBooks />} />
              <Route path="/create-book" element={<CreateBook />} />
              <Route path="/create-member" element={<CreateMember />} />
              <Route path="/borrow-book" element={<BorrowBook />} />
            </Routes>
          </div>
          
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
