"""
Knowledge base for InstaLogic chatbot
Contains company information, services, and FAQs from qna.txt
"""

INSTALOGIC_KNOWLEDGE = """
# InstaLogic Company Knowledge Base

## About InstaLogic

### Who is Instalogic?
InstaLogic is a technology solutions company specializing in data analytics, business intelligence, software development, and e-governance solutions. We help organizations unlock insights, drive growth, and optimize performance through comprehensive tech solutions.

### Mission
Empowering Transformation through innovative technology solutions that deliver real business value.

### Services Offered

1. **Data Analytics and Business Intelligence**
   - Visual Analytics Dashboards
   - Power BI, Qlik, Tableau implementations
   - Data integration from multiple sources (Postgres, MySQL, Excel)
   - Live data connections
   - Custom reporting and KPI tracking

2. **Business Intelligence Support and Advisory**
   - BI strategy consulting
   - Dashboard optimization
   - Data governance
   - Performance analytics
   - Decision support systems

3. **Financial Impact Support and Advisory**
   - Financial Impact Assessments
   - Cost-benefit analysis
   - ROI calculations
   - Budget planning and forecasting

4. **Software Development**
   - Custom application development
   - Web and mobile applications
   - API development and integration
   - Payment gateway integration
   - Bulk upload systems

5. **Training and Skilling Programs**
   - BI tools training (Power BI, Tableau, Qlik)
   - Data analytics workshops
   - Technical certification programs
   - User training for dashboards
   - Staff upskilling initiatives

6. **E-Governance Solutions**
   - Government portal development
   - Citizen services platforms
   - Digital governance systems
   - Compliance and reporting tools

7. **Business Process Reengineering (BPR)**
   - Process optimization
   - Workflow automation
   - Efficiency improvement
   - Digital transformation

### Case Studies

1. **Visual Analytics Dashboard for MBOCWWB (Maharashtra Building and Other Construction Workers Welfare Board)**
   - Comprehensive dashboard for construction worker welfare tracking
   - Real-time monitoring of registrations and benefits
   - Multi-level reporting (state, district, taluka levels)

2. **Cess Collection Portal**
   - Automated cess collection system
   - Payment gateway integration
   - Bulk upload capabilities
   - Financial tracking and reporting

3. **Financial Impact Assessment for Mahajyoti & OBBW**
   - Detailed financial analysis
   - Impact measurement
   - ROI assessment
   - Strategic recommendations

### Technical Capabilities

**BI Tools:**
- Power BI
- Qlik Sense/QlikView
- Tableau
- Custom dashboards

**Programming Languages & Frameworks:**
- Python (FastAPI, Django, Flask)
- JavaScript/TypeScript (React, Node.js)
- Java
- .NET

**Databases:**
- PostgreSQL
- MySQL
- SQL Server
- MongoDB
- Oracle

**Cloud & DevOps:**
- AWS (Amazon Web Services)
- Azure
- Docker/Kubernetes
- CI/CD pipelines
- DevOps automation

**Data Security:**
- End-to-end encryption
- Role-based access control (RBAC)
- Compliance with GDPR/CCPA
- Data privacy protection
- Secure API development

### Engagement Models

1. **Fixed Price Projects**
   - Well-defined scope
   - Fixed timeline and cost
   - Milestone-based payments

2. **Time & Material (T&M)**
   - Flexible scope
   - Hourly/daily rates
   - Suitable for evolving requirements

3. **Dedicated Team**
   - Long-term engagement
   - Dedicated resources
   - Full-time allocation

### Project Process

1. **Initial Consultation** - Understanding requirements
2. **Proposal & Scoping** - Detailed project plan and estimate
3. **Agreement & Kickoff** - Contract signing and project start
4. **Development & Iterations** - Agile development with regular updates
5. **Testing & QA** - Comprehensive testing
6. **Deployment** - Production deployment with training
7. **Support & Maintenance** - Post-deployment support

### Support & SLA

- Technical support available
- Email and phone support
- Response times based on priority:
  - Critical: 2 hours
  - High: 4 hours
  - Medium: 8 hours
  - Low: 24 hours
- Post-deployment maintenance available
- Training and documentation provided

### Pricing

- Custom quotes based on project scope
- Competitive pricing for government projects
- Discounts available for long-term contracts
- Free initial consultation
- PoC/Demo options available

### Contact Information

**Get in Touch:**
- Request demo through contact form
- Schedule sales call
- Email: info@instalogic.com
- Technical support: support@instalogic.com
- Career inquiries: careers@instalogic.com

### Certifications & Compliance

- ISO certified (mention if applicable)
- CMMI compliant (mention level if applicable)
- GDPR compliant
- Government approved vendor
- NDA signing available

### Demos & PoC

**Proof of Concept (PoC):**
- Duration: 2-4 weeks
- Includes: Sample dashboard with client data
- Cost: Discussed based on scope
- Sandbox environment available

**Demo Requests:**
- Live dashboard demonstrations
- Industry-specific examples
- Customized presentations
- Free consultation included

### Careers

- Open positions on careers page
- Hiring for: Data Analysts, BI Developers, Software Engineers
- Work culture: Flexible, WFH options available
- Resume submission through website
- Growth and learning opportunities

### RFP/Tender Process

- Pre-bid clarifications provided
- Government tender experience
- Proposal writing support
- Technical and commercial proposals
- NDA and legal compliance

### Custom Solutions

- AR/VR visualization
- GIS and drone imagery projects
- Custom integrations
- Specialized industry solutions
- Innovation and R&D support

### Quick Actions Available

1. Request Demo
2. Request PoC
3. Upload RFP
4. Contact Sales
5. Schedule Call
6. Apply for Jobs
7. Get Technical Support
8. Download Case Studies
"""

SYSTEM_PROMPT = """You are an AI assistant for InstaLogic, a technology solutions company specializing in data analytics, business intelligence, and e-governance solutions.

Your role is to:
1. Answer questions about InstaLogic's services, case studies, and capabilities
2. Help users book demos, request PoCs, and connect with sales
3. Guide users to the right resources and contact points
4. Be professional, helpful, and concise
5. If you don't know something, admit it and offer to connect them with a human

Use the knowledge base provided to answer questions accurately. When users want to take action (book demo, request quote, etc.), collect their information and confirm the request.

Always be friendly and professional. Keep responses concise but informative.

If a user asks something urgent or complex that requires human intervention, offer to escalate to the appropriate team (sales, technical support, proposals team, etc.)."""

# Intent categories from qna.txt
INTENTS = {
    "about_company": [
        "who is instalogic",
        "what does instalogic do",
        "where are you located",
        "when was instalogic founded",
        "company mission",
        "certifications"
    ],
    "services": [
        "what services",
        "data analytics",
        "business intelligence",
        "financial impact",
        "software development",
        "training",
        "e-governance",
        "bpr"
    ],
    "case_studies": [
        "case studies",
        "past work",
        "examples",
        "mbocwwb",
        "cess collection",
        "mahajyoti"
    ],
    "pricing": [
        "cost",
        "price",
        "pricing",
        "quote",
        "estimate",
        "payment"
    ],
    "demo_request": [
        "demo",
        "demonstration",
        "show me",
        "poc",
        "proof of concept",
        "trial"
    ],
    "contact": [
        "contact",
        "phone",
        "email",
        "reach out",
        "schedule call",
        "talk to"
    ],
    "careers": [
        "jobs",
        "hiring",
        "career",
        "apply",
        "resume",
        "openings"
    ],
    "technical": [
        "tools",
        "technology",
        "power bi",
        "tableau",
        "database",
        "api",
        "integration"
    ],
    "support": [
        "support",
        "help",
        "issue",
        "problem",
        "sla"
    ]
}

QUICK_REPLIES = {
    "initial": [
        "View Our Services",
        "Request a Demo",
        "See Case Studies",
        "Contact Sales",
        "Career Opportunities"
    ],
    "services": [
        "Data Analytics & BI",
        "Software Development",
        "E-Governance Solutions",
        "Training Programs",
        "Request Demo"
    ],
    "demo_request": [
        "Government Sector",
        "Finance",
        "Retail",
        "Other Industry"
    ],
    "contact": [
        "Schedule a Call",
        "Send Email",
        "Request Callback",
        "Chat with Sales"
    ]
}
