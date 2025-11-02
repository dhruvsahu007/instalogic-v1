import './Hero.css'

function Hero() {
  return (
    <section id="home" className="hero">
      <div className="hero-overlay"></div>
      <div className="container">
        <div className="hero-content">
          <h1 className="hero-title">
            Empowering<br />
            <span className="highlight">Transformation</span>
          </h1>
          <p className="hero-subtitle">
            Unlock Insights, Drive Growth And Optimize Performance With Comprehensive Tech Solutions.
          </p>
          <button className="cta-button">Explore Now</button>
        </div>
      </div>
    </section>
  )
}

export default Hero
