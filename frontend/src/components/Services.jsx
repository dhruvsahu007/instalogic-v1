import './Services.css'

function Services({ services }) {
  return (
    <section id="services" className="services">
      <div className="container">
        <div className="services-grid">
          {services.map((service) => (
            <div key={service.id} className="service-card">
              <span className="service-number">{service.number}</span>
              <h3>{service.title}</h3>
              {service.description && <p>{service.description}</p>}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Services
