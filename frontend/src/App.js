import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ErrorBoundary from './components/ErrorBoundary';
import routes from './routes';

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
              {routes.map(route => (
                <Route key={route.path} path={route.path} element={route.element} />
              ))}
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
