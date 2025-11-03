import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Services from './components/Services'
import About from './components/About'
import Contact from './components/Contact'
import Footer from './components/Footer'
import Sidebar from './components/Sidebar'
import Chatbot from './components/Chatbot'
import Dashboard from './pages/admin/Dashboard'
import Leads from './pages/admin/Leads'
import PriorityQueue from './pages/admin/PriorityQueue'
import './App.css'

function HomePage() {
  const [services, setServices] = useState([])

  useEffect(() => {
    // Fetch services from API
    fetch('/api/services')
      .then(res => res.json())
      .then(data => setServices(data.services))
      .catch(err => console.error('Error fetching services:', err))
  }, [])

  return (
    <>
      <Navbar />
      <Hero />
      <Sidebar />
      <Services services={services} />
      <About />
      <Contact />
      <Footer />
      <Chatbot />
    </>
  )
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admin/dashboard" element={<Dashboard />} />
          <Route path="/admin/leads" element={<Leads />} />
          <Route path="/admin/priority-queue" element={<PriorityQueue />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
