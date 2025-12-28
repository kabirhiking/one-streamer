import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

const Header = () => {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <h1>VideoStream</h1>
        </Link>

        <nav className="nav">
          {user ? (
            <>
              <Link to="/upload" className="nav-link">Upload</Link>
              {user.is_creator && (
                <Link to="/dashboard" className="nav-link">Dashboard</Link>
              )}
              <Link to="/profile" className="nav-link">Profile</Link>
              <button onClick={logout} className="nav-link btn-link">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link btn-primary">Sign Up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
