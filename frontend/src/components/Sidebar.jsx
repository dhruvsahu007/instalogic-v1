import './Sidebar.css'

function Sidebar() {
  const scrollToContact = () => {
    const element = document.getElementById('contact')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div className="sidebar-touch" onClick={scrollToContact}>
      <span>Get In Touch</span>
    </div>
  )
}

export default Sidebar
