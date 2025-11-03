from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
import uuid

from bedrock_client import BedrockClient
from knowledge_base import INSTALOGIC_KNOWLEDGE, SYSTEM_PROMPT, QUICK_REPLIES
from chatbot_orchestrator import create_orchestrator
from database_service import database_service

app = FastAPI(title="InstaLogic API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client and orchestrator
bedrock_client = BedrockClient()
orchestrator = create_orchestrator(bedrock_client)

# In-memory storage (replace with database in production)
contact_messages = []
chat_sessions = {}  # Store chat history by session_id
demo_requests = []
services = [
    {
        "id": 1,
        "number": "01",
        "title": "Data Analytics and Business Intelligence",
        "description": "Transform your data into actionable insights with our comprehensive analytics solutions."
    },
    {
        "id": 2,
        "number": "02",
        "title": "Business Intelligence Support and Advisory",
        "description": "Expert guidance to help you make data-driven decisions and optimize your business processes."
    },
    {
        "id": 3,
        "number": "03",
        "title": "Financial Impact Support and Advisory",
        "description": "Maximize your financial performance with our strategic advisory services."
    },
    {
        "id": 4,
        "number": "04",
        "title": "E-Governance Solutions",
        "description": "Modern digital solutions for efficient government operations and citizen services."
    }
]

# Models
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str

class Service(BaseModel):
    id: int
    number: str
    title: str
    description: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    quick_replies: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    timestamp: str

class DemoRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: str
    message: Optional[str] = None
    preferred_date: Optional[str] = None

class RFPUpload(BaseModel):
    name: str
    email: EmailStr
    company: str
    phone: Optional[str] = None
    project_brief: str
    timeline: Optional[str] = None
    budget_range: Optional[str] = None

# Helper functions
def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Get existing session or create new one"""
    if session_id and session_id in chat_sessions:
        return session_id
    
    new_session_id = str(uuid.uuid4())
    chat_sessions[new_session_id] = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    }
    return new_session_id

def add_to_history(session_id: str, role: str, content: str):
    """Add message to conversation history"""
    if session_id in chat_sessions:
        chat_sessions[session_id]["messages"].append({
            "role": role,
            "content": content
        })
        chat_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        # Keep only last 10 messages to avoid token limits
        if len(chat_sessions[session_id]["messages"]) > 20:  # 10 user + 10 assistant
            chat_sessions[session_id]["messages"] = chat_sessions[session_id]["messages"][-20:]

def detect_intent(message: str) -> str:
    """Simple intent detection based on keywords"""
    message_lower = message.lower()
    
    # Demo/PoC requests
    if any(word in message_lower for word in ["demo", "demonstration", "poc", "proof of concept", "trial"]):
        return "demo_request"
    
    # Contact/sales
    if any(word in message_lower for word in ["contact", "call", "speak to", "human", "sales"]):
        return "contact"
    
    # Services
    if any(word in message_lower for word in ["service", "what do you", "capabilities", "offerings"]):
        return "services"
    
    # Case studies
    if any(word in message_lower for word in ["case study", "case studies", "example", "past work", "portfolio"]):
        return "case_studies"
    
    # Pricing
    if any(word in message_lower for word in ["price", "cost", "pricing", "quote", "estimate"]):
        return "pricing"
    
    # Careers
    if any(word in message_lower for word in ["career", "job", "hiring", "apply", "resume"]):
        return "careers"
    
    return "general"

# Routes

async def root():
    return {
        "message": "Welcome to InstaLogic API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/services")
async def get_services():
    """Get all services"""
    return {"services": services}

@app.get("/api/services/{service_id}")
async def get_service(service_id: int):
    """Get a specific service by ID"""
    service = next((s for s in services if s["id"] == service_id), None)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.post("/api/contact")
async def submit_contact(contact: ContactMessage):
    """Submit a contact form message"""
    message_data = contact.dict()
    contact_messages.append(message_data)
    return {
        "success": True,
        "message": "Thank you for your message! We will get back to you soon.",
        "data": message_data
    }

@app.get("/api/contact/messages")
async def get_contact_messages():
    """Get all contact messages (admin endpoint)"""
    return {"messages": contact_messages, "count": len(contact_messages)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "source_filter": "STRICT_MODE_v2_DEBUG",  # Indicator that new code is loaded
        "timestamp": datetime.now().isoformat()
    }

# ============= CHATBOT ENDPOINTS =============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Main chatbot endpoint - uses orchestrator for intelligent routing
    Routes to either transactional flows or Knowledge Base queries
    """
    try:
        # Get or create session
        session_id = get_or_create_session(chat_message.session_id)
        user_message = chat_message.message
        
        # Add user message to history
        add_to_history(session_id, "user", user_message)
        
        # Use orchestrator to handle the query
        orchestrator_result = orchestrator.handle_user_query(user_message, session_id)
        
        # Extract response based on orchestrator result type
        ai_response = orchestrator_result['response']
        sources = orchestrator_result.get('sources', [])
        rich_payload = orchestrator_result.get('rich_payload', {})
        
        # Convert rich payload buttons to quick replies
        quick_replies_list = []
        if rich_payload and 'buttons' in rich_payload:
            quick_replies_list = [btn['label'] for btn in rich_payload['buttons'][:4]]
        
        # If no quick replies from orchestrator, use intent detection fallback
        if not quick_replies_list:
            intent = detect_intent(user_message)
            quick_replies_list = QUICK_REPLIES.get(intent, QUICK_REPLIES["initial"])
        
        # Add AI response to history
        add_to_history(session_id, "assistant", ai_response)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            quick_replies=quick_replies_list,
            sources=sources if sources else None,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id]["messages"],
        "created_at": chat_sessions[session_id]["created_at"],
        "last_activity": chat_sessions[session_id]["last_activity"]
    }

@app.delete("/api/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"success": True, "message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/demo-request")
async def request_demo(demo: DemoRequest):
    """Submit a demo request"""
    demo_data = demo.dict()
    demo_data["timestamp"] = datetime.now().isoformat()
    demo_data["id"] = str(uuid.uuid4())
    demo_requests.append(demo_data)
    
    return {
        "success": True,
        "message": f"Thank you {demo.name}! Your demo request has been received. We'll contact you soon.",
        "request_id": demo_data["id"]
    }

@app.get("/api/demo-requests")
async def get_demo_requests():
    """Get all demo requests (admin endpoint)"""
    return {"requests": demo_requests, "count": len(demo_requests)}

@app.post("/api/rfp-upload")
async def upload_rfp(rfp: RFPUpload):
    """Submit an RFP"""
    rfp_data = rfp.dict()
    rfp_data["timestamp"] = datetime.now().isoformat()
    rfp_data["id"] = str(uuid.uuid4())
    
    return {
        "success": True,
        "message": f"Thank you {rfp.name}! Your RFP has been received. Our proposals team will review it and get back to you within 24-48 hours.",
        "rfp_id": rfp_data["id"]
    }

@app.get("/api/chat/sessions")
async def get_all_sessions():
    """Get all active chat sessions (admin endpoint)"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(data["messages"]),
                "created_at": data["created_at"],
                "last_activity": data["last_activity"]
            }
            for sid, data in chat_sessions.items()
        ],
        "total": len(chat_sessions)
    }

# ============= END CHATBOT ENDPOINTS =============

# ============= ADMIN ENDPOINTS FOR LEADS =============

@app.get("/api/leads")
async def get_all_leads(status: Optional[str] = None):
    """Get all leads from database, optionally filtered by status"""
    try:
        leads = database_service.get_all_leads(status)
        return {
            "success": True,
            "leads": leads,
            "count": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")

@app.get("/api/leads/statistics")
async def get_lead_statistics():
    """Get lead statistics"""
    try:
        stats = database_service.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: int):
    """Get a specific lead by ID"""
    try:
        lead = database_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {
            "success": True,
            "lead": lead
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lead: {str(e)}")

@app.put("/api/leads/{lead_id}/status")
async def update_lead_status(lead_id: int, status: str):
    """Update lead status"""
    try:
        valid_statuses = ["NEW", "CONTACTED", "IN_PROGRESS", "CLOSED"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        success = database_service.update_lead_status(lead_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "message": f"Lead status updated to {status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

@app.put("/api/leads/{lead_id}/notes")
async def update_lead_notes(lead_id: int, notes: str):
    """Update admin notes for a lead"""
    try:
        success = database_service.update_lead_notes(lead_id, notes)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "message": "Lead notes updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notes: {str(e)}")

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: int):
    """Delete a lead (use with caution)"""
    try:
        success = database_service.delete_lead(lead_id)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "message": "Lead deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting lead: {str(e)}")

# ============= END ADMIN ENDPOINTS =============

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
