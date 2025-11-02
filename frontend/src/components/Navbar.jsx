import { useState } from 'react'
import './Navbar.css'

function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  const scrollToSection = (id) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setIsOpen(false)
    }
  }

  return (
    <nav className="navbar">
      <div className="container">
        <div className="logo">
          <img src="https://via.placeholder.com/150x50/4A90E2/FFFFFF?text=INSTALOGIC" alt="InstaLogic Logo" />
        </div>
        
        <div className={`nav-menu ${isOpen ? 'active' : ''}`}>
          <button onClick={() => scrollToSection('home')}>Discover Our Work</button>
          <button onClick={() => scrollToSection('story')}>Our Story</button>
          <button onClick={() => scrollToSection('services')}>Our Services</button>
          <button onClick={() => scrollToSection('careers')}>Careers</button>
          <button onClick={() => scrollToSection('blog')}>Blog</button>
          <button onClick={() => scrollToSection('contact')}>Contact Us</button>
        </div>
        
        <div className="nav-icons">
          <div className="search-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          <div className="hamburger" onClick={() => setIsOpen(!isOpen)}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
