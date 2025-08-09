// components/Navigation.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* <Link to="/" className="nav-logo">
          Restaurant Manager
        </Link> */}
        
        
          <div className={`hamburger ${isOpen ? 'active' : ''}`} onClick={toggleMenu}>
          <span></span>
          <span></span>
          <span></span>
        </div>
        
        <ul className={`nav-menu ${isOpen ? 'active' : ''}`}>
          {/* <li className="nav-item">
            <Link to="/form" className="nav-link" onClick={toggleMenu}>
              Add Restaurant
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/view" className="nav-link" onClick={toggleMenu}>
              View All
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/delete" className="nav-link" onClick={toggleMenu}>
              Delete Restaurant
            </Link>
          </li> */}
          <li className="nav-item">
            <Link to="/investment" className="nav-link" onClick={toggleMenu}>
              Add Investment Statement
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navigation;