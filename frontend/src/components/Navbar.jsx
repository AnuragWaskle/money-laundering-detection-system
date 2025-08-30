import React from 'react';
import '../assets/Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <svg 
          className="navbar-logo"
          width="40" 
          height="40" 
          viewBox="0 0 24 24" 
          strokeWidth="2" 
          stroke="currentColor" 
          fill="none" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M9 12l-4.463 4.463a5 5 0 1 0 7.072 -7.072l-4.463 4.463" />
          <path d="M15 12l4.463 -4.463a5 5 0 1 0 -7.072 7.072l4.463 -4.463" />
        </svg>
        <h1>AML Guardian</h1>
      </div>
      <div className="navbar-links">
        <a href="/" className="nav-link">Global Dashboard</a>
        <a href="/cases" className="nav-link">Case Management</a>
        <a href="/trace" className="nav-link">Trace & Investigate</a>
        <a href="#contact" className="nav-link contact-link">Contact</a>
      </div>
    </nav>
  );
};

export default Navbar;
