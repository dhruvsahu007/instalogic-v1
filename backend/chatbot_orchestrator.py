"""
Chatbot Orchestration Layer for AWS Bedrock Knowledge Base
Handles routing between transactional flows and knowledge queries
"""
import re
import uuid
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from bedrock_client import BedrockClient

# Import Database service for saving leads
try:
    from database_service import database_service
    DATABASE_ENABLED = True
except ImportError:
    DATABASE_ENABLED = False
    print("⚠️  Database service not available - leads will not be saved")


class SessionManager:
    """Manages conversation state for multi-turn flows"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def get_session(self, session_id: str) -> Dict:
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'state': None,
                'data': {},
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, state: str, data: Dict):
        """Update session state and data"""
        session = self.get_session(session_id)
        session['state'] = state
        session['data'].update(data)
        session['last_updated'] = datetime.now().isoformat()
    
    def clear_session_state(self, session_id: str):
        """Clear conversation state (keep session alive)"""
        if session_id in self.sessions:
            self.sessions[session_id]['state'] = None
            self.sessions[session_id]['data'] = {}


class ChatbotOrchestrator:
    """
    Main orchestration layer that routes between:
    1. High-priority human handoff
    2. Transactional flows (demo, careers, RFP)
    3. Knowledge Base queries
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock_client = bedrock_client
        self.session_manager = SessionManager()
        
        # Define transactional intent patterns
        self.transactional_patterns = {
            'request_demo': [
                r'\b(book|request|schedule|want|need|get)\s+(a\s+)?(demo|demonstration|poc|proof of concept)\b',
                r'\bshow\s+me\s+(a\s+)?demo\b',
                r'\bcan\s+i\s+(see|get|have)\s+(a\s+)?demo\b'
            ],
            'request_career': [
                r'\b(apply|submit|upload|send)\s+(my\s+)?(resume|cv|application)\b',
                r'\b(are\s+you\s+)?hiring\b',
                r'\bjob\s+(opening|opportunity|application|position)\b',
                r'\bcareer\s+(opportunity|page)\b',
                r'\bhow\s+(do|can)\s+i\s+apply\b'
            ],
            'upload_rfp': [
                r'\b(upload|submit|send|share)\s+(an\s+|my\s+|our\s+)?rfp\b',
                r'\b(have|got)\s+(an\s+)?rfp\b',
                r'\bproposal\s+request\b',
                r'\brequest\s+for\s+proposal\b'
            ],
            'request_contact': [
                r'\b(contact|call|speak\s+to|talk\s+to)\s+(sales|team|someone)\b',
                r'\bschedule\s+(a\s+)?(call|meeting)\b',
                r'\bget\s+in\s+touch\b'
            ]
        }
        
        # Human handoff patterns (highest priority)
        self.handoff_patterns = [
            r'\b(speak|talk)\s+to\s+(a\s+)?(human|person|agent|representative)\b',
            r'\bconnect\s+me\s+to\s+(support|human|agent|someone)\b',
            r'\b(urgent|emergency|critical)\s+(issue|problem|matter)\b',
            r'\bneed\s+(immediate|urgent)\s+help\b',
            r'\bescalate\b',
            r'\bhuman\s+(agent|support)\b'
        ]
        
        # Topic keywords for enriching responses
        self.topic_keywords = {
            'careers': ['job', 'career', 'hiring', 'apply', 'resume', 'position', 'opening', 'work at'],
            'demo': ['demo', 'demonstration', 'poc', 'proof of concept', 'trial', 'sandbox'],
            'services': ['service', 'offering', 'capability', 'solution', 'provide', 'deliver'],
            'case_studies': ['case study', 'case studies', 'past work', 'project', 'client example'],
            'pricing': ['price', 'cost', 'pricing', 'budget', 'estimate', 'quotation'],
            'contact': ['contact', 'reach', 'phone', 'email', 'address', 'location', 'office'],
            'technical': ['tool', 'technology', 'framework', 'database', 'integration', 'api'],
            'procurement': ['rfp', 'proposal', 'tender', 'procurement', 'bid']
        }
    
    def handle_user_query(self, query: str, session_id: str) -> Dict:
        """
        Main router function - OUTPUT 1
        Routes query to appropriate handler based on intent detection
        
        Priority:
        1. Human handoff (highest priority)
        2. Active multi-turn flow
        3. Transactional intent
        4. Knowledge Base query
        """
        query_lower = query.lower().strip()
        
        # ========================================
        # PRIORITY 1: Human Handoff (OUTPUT 4)
        # ========================================
        if self._detect_handoff(query_lower):
            return self._escalate_to_human(query, session_id)
        
        # ========================================
        # PRIORITY 2: Active Multi-Turn Flow
        # ========================================
        session = self.session_manager.get_session(session_id)
        if session['state'] is not None:
            # Continue existing flow
            if session['state'].startswith('demo_'):
                return self.handle_demo_flow(query, session_id)
            elif session['state'].startswith('career_'):
                return self.handle_career_flow(query, session_id)
            elif session['state'].startswith('rfp_'):
                return self.handle_rfp_flow(query, session_id)
            elif session['state'].startswith('contact_'):
                return self.handle_contact_flow(query, session_id)
        
        # ========================================
        # PRIORITY 3: Transactional Intent Detection
        # ========================================
        intent = self._detect_transactional_intent(query_lower)
        
        if intent == 'request_demo':
            return self.handle_demo_flow(query, session_id)
        elif intent == 'request_career':
            return self.handle_career_flow(query, session_id)
        elif intent == 'upload_rfp':
            return self.handle_rfp_flow(query, session_id)
        elif intent == 'request_contact':
            return self.handle_contact_flow(query, session_id)
        
        # ========================================
        # PRIORITY 4: Knowledge Base Query
        # ========================================
        return self._query_knowledge_base(query, session_id)
    
    def _detect_handoff(self, query: str) -> bool:
        """
        OUTPUT 4: Detect human handoff triggers
        High-priority check before all other processing
        """
        for pattern in self.handoff_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _escalate_to_human(self, query: str, session_id: str) -> Dict:
        """
        OUTPUT 4: Handle human handoff
        Immediately escalate without processing further
        """
        ticket_id = str(uuid.uuid4())[:8].upper()
        
        # Save handoff lead to database
        if DATABASE_ENABLED:
            lead_data = database_service.format_handoff_lead(query, ticket_id)
            database_service.save_lead(lead_data)
        
        # Clear any active flow
        self.session_manager.clear_session_state(session_id)
        
        return {
            'type': 'handoff',
            'response': "I understand you'd like to speak with a human agent. Let me connect you with our support team right away.",
            'action': 'escalate_to_human',
            'ticket_id': ticket_id,
            'metadata': {
                'escalation_reason': 'user_request',
                'original_query': query,
                'priority': 'high'
            },
            'rich_payload': {
                'buttons': [
                    {'label': '📞 Call Us', 'action': 'show_phone', 'value': '+1-XXX-XXX-XXXX'},
                    {'label': '✉️ Email Us', 'action': 'show_email', 'value': 'support@instalogic.in'}
                ],
                'message': f"Your escalation ticket ID is **{ticket_id}**. A team member will contact you shortly."
            }
        }
    
    def _detect_transactional_intent(self, query: str) -> Optional[str]:
        """Detect if query matches transactional patterns"""
        for intent, patterns in self.transactional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        return None
    
    def _query_knowledge_base(self, query: str, session_id: str) -> Dict:
        """
        Query Bedrock Knowledge Base and enrich response
        Combines KB query with rich actionable responses (OUTPUT 3)
        """
        # Concise system prompt with first-person instructions
        concise_prompt = """You are InstaLogic's AI assistant. You represent the company directly.

CRITICAL RULES:
1. Speak in FIRST PERSON - use "we", "our", "us" (NOT "InstaLogic's")
2. NEVER say "Based on the context provided" or similar phrases
3. Keep responses SHORT (2-3 sentences max)
4. Use bullet points for lists (max 4 items)
5. Be natural and conversational

Examples:
❌ BAD: "InstaLogic's services include..." or "Based on the context..."
✅ GOOD: "We offer..." or "Our services include..."

Be brief, warm, and professional."""
        
        # Query Bedrock KB
        kb_result = self.bedrock_client.generate_response_with_kb(
            user_message=query,
            system_prompt=concise_prompt,
            use_knowledge_base=True
        )
        
        # Enrich response with actions (OUTPUT 3)
        enriched_response = self.enrich_response(kb_result['response'], query)
        
        return {
            'type': 'knowledge',
            'response': kb_result['response'],
            'sources': kb_result.get('sources', []),
            'rich_payload': enriched_response,
            'metadata': {
                'kb_used': kb_result.get('context_used', False),
                'source_count': len(kb_result.get('sources', []))
            }
        }
    
    def enrich_response(self, kb_response: str, user_query: str) -> Dict:
        """
        OUTPUT 3: Enrich KB response with rich actions
        Adds buttons/forms based on detected topic
        """
        combined_text = (user_query + ' ' + kb_response).lower()
        
        # Detect primary topic
        detected_topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_topics.append(topic)
        
        # Build rich payload based on detected topics
        buttons = []
        additional_message = None
        
        if 'careers' in detected_topics:
            buttons.extend([
                {'label': '📄 Upload Resume', 'action': 'show_resume_form'},
                {'label': '💼 View Open Positions', 'action': 'open_link', 'url': 'https://www.instalogic.in/careers/'}
            ])
            additional_message = "Interested in joining our team? Upload your resume to apply!"
        
        if 'demo' in detected_topics:
            buttons.extend([
                {'label': '🎯 Request Demo', 'action': 'start_demo_flow'},
                {'label': '🔬 Request PoC', 'action': 'start_demo_flow'}
            ])
        
        if 'services' in detected_topics:
            buttons.extend([
                {'label': '📋 View All Services', 'action': 'open_link', 'url': 'https://www.instalogic.in/our-services/'},
                {'label': '🎯 Request Demo', 'action': 'start_demo_flow'},
                {'label': '📞 Contact Sales', 'action': 'start_contact_flow'}
            ])
        
        if 'case_studies' in detected_topics:
            buttons.extend([
                {'label': '📚 View Case Studies', 'action': 'open_link', 'url': 'https://www.instalogic.in/case-studies/'},
                {'label': '🎯 Request Demo', 'action': 'start_demo_flow'}
            ])
        
        if 'pricing' in detected_topics:
            buttons.extend([
                {'label': '💰 Get Quote', 'action': 'start_contact_flow'},
                {'label': '📊 Request Estimate', 'action': 'start_demo_flow'}
            ])
        
        if 'contact' in detected_topics:
            buttons.extend([
                {'label': '📞 Schedule Call', 'action': 'start_contact_flow'},
                {'label': '✉️ Contact Us', 'action': 'open_link', 'url': 'https://www.instalogic.in/contact-us/'}
            ])
        
        if 'procurement' in detected_topics:
            buttons.extend([
                {'label': '📤 Upload RFP', 'action': 'start_rfp_flow'},
                {'label': '📝 Request NDA', 'action': 'start_contact_flow'}
            ])
        
        # Add general buttons if no specific topic detected
        if not buttons:
            buttons = [
                {'label': '📋 View Services', 'action': 'open_link', 'url': 'https://www.instalogic.in/our-services/'},
                {'label': '🎯 Request Demo', 'action': 'start_demo_flow'},
                {'label': '📞 Contact Sales', 'action': 'start_contact_flow'}
            ]
        
        return {
            'buttons': buttons[:4],  # Limit to 4 buttons to avoid clutter
            'additional_message': additional_message
        }
    
    # ========================================
    # OUTPUT 2: Multi-Turn Transactional Flows
    # ========================================
    
    def handle_demo_flow(self, query: str, session_id: str) -> Dict:
        """
        OUTPUT 2: Multi-turn demo request flow with state management
        
        Flow steps:
        1. demo_start -> Ask for industry
        2. demo_awaiting_industry -> Ask for name (or custom industry if "Other")
        2b. demo_awaiting_custom_industry -> Collect custom industry, then ask for name
        3. demo_awaiting_name -> Ask for email
        4. demo_awaiting_email -> Ask for phone
        5. demo_awaiting_phone -> Ask for referral source
        6. demo_awaiting_referral -> Ask for date (or custom referral if "Other")
        6b. demo_awaiting_custom_referral -> Collect custom referral, then ask for date
        7. demo_awaiting_date -> Confirm and complete
        """
        session = self.session_manager.get_session(session_id)
        current_state = session['state']
        
        # Step 1: Start flow - Ask for industry
        if current_state is None or current_state == 'demo_start':
            self.session_manager.update_session(session_id, 'demo_awaiting_industry', {})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': "I'd be happy to arrange a demo! 🎯\n\nWhich industry is this for?",
                'rich_payload': {
                    'buttons': [
                        {'label': '🏛️ Government', 'action': 'select_industry', 'value': 'Government'},
                        {'label': '💼 Finance', 'action': 'select_industry', 'value': 'Finance'},
                        {'label': '🛒 Retail', 'action': 'select_industry', 'value': 'Retail'},
                        {'label': '🏢 Other', 'action': 'select_industry', 'value': 'Other'}
                    ]
                },
                'metadata': {'step': 1, 'total_steps': 7}
            }
        
        # Step 2: Collect industry -> Ask for name (or ask for specific industry if "Other")
        elif current_state == 'demo_awaiting_industry':
            industry = query.strip()
            
            # If "Other" is selected, ask for specific industry
            if '🏢 Other' in industry or industry.lower() == 'other':
                self.session_manager.update_session(session_id, 'demo_awaiting_custom_industry', {})
                return {
                    'type': 'transaction',
                    'flow': 'demo',
                    'response': "Great! 👍\n\nWhich industry would you like the demo for? (Please specify)",
                    'rich_payload': {'input_type': 'text', 'placeholder': 'e.g., Healthcare, Manufacturing, etc.'},
                    'metadata': {'step': 2, 'total_steps': 7}
                }
            
            # Standard industry selected
            self.session_manager.update_session(session_id, 'demo_awaiting_name', {'industry': industry})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': f"Great! **{industry}** industry. 👍\n\nWhat's your name?",
                'rich_payload': {'input_type': 'text', 'placeholder': 'Your full name'},
                'metadata': {'step': 2, 'total_steps': 7}
            }
        
        # Step 2b: Collect custom industry (when "Other" was selected)
        elif current_state == 'demo_awaiting_custom_industry':
            custom_industry = query.strip()
            self.session_manager.update_session(session_id, 'demo_awaiting_name', {'industry': custom_industry})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': f"Perfect! **{custom_industry}** industry. 👍\n\nWhat's your name?",
                'rich_payload': {'input_type': 'text', 'placeholder': 'Your full name'},
                'metadata': {'step': 2, 'total_steps': 7}
            }
        
        # Step 3: Collect name -> Ask for email
        elif current_state == 'demo_awaiting_name':
            name = query.strip()
            self.session_manager.update_session(session_id, 'demo_awaiting_email', {'name': name})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': f"Nice to meet you, **{name}**! 👋\n\nWhat's your email?",
                'rich_payload': {'input_type': 'email', 'placeholder': 'your.email@company.com'},
                'metadata': {'step': 3, 'total_steps': 7}
            }
        
        # Step 4: Collect email -> Ask for phone
        elif current_state == 'demo_awaiting_email':
            email = query.strip()
            # Basic email validation
            if '@' not in email or '.' not in email:
                return {
                    'type': 'transaction',
                    'flow': 'demo',
                    'response': "Please provide a valid email:",
                    'rich_payload': {'input_type': 'email', 'placeholder': 'your.email@company.com'},
                    'metadata': {'step': 3, 'total_steps': 7, 'error': True}
                }
            
            self.session_manager.update_session(session_id, 'demo_awaiting_phone', {'email': email})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': "Perfect! 📧\n\nWhat's your phone number?",
                'rich_payload': {'input_type': 'tel', 'placeholder': '+91 XXXXX XXXXX'},
                'metadata': {'step': 4, 'total_steps': 7}
            }
        
        # Step 5: Collect phone -> Ask how they heard about us
        elif current_state == 'demo_awaiting_phone':
            phone = query.strip()
            self.session_manager.update_session(session_id, 'demo_awaiting_referral', {'phone': phone})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': "Thanks! 📱\n\nHow did you hear about us?",
                'rich_payload': {
                    'buttons': [
                        {'label': '🔍 Google Search', 'action': 'select_referral', 'value': 'Google Search'},
                        {'label': '🤝 Referral', 'action': 'select_referral', 'value': 'Referral'},
                        {'label': '📱 Social Media', 'action': 'select_referral', 'value': 'Social Media'},
                        {'label': '📰 Advertisement', 'action': 'select_referral', 'value': 'Advertisement'},
                        {'label': '🏢 Other', 'action': 'select_referral', 'value': 'Other'}
                    ]
                },
                'metadata': {'step': 5, 'total_steps': 7}
            }
        
        # Step 6: Collect referral source -> Ask for date (or ask for specific source if "Other")
        elif current_state == 'demo_awaiting_referral':
            referral_source = query.strip()
            
            # If "Other" is selected, ask for specific source
            if '🏢 Other' in referral_source or referral_source.lower() == 'other':
                self.session_manager.update_session(session_id, 'demo_awaiting_custom_referral', {})
                return {
                    'type': 'transaction',
                    'flow': 'demo',
                    'response': "Thanks! 👍\n\nHow did you hear about us? (Please specify)",
                    'rich_payload': {'input_type': 'text', 'placeholder': 'e.g., LinkedIn, Blog, Conference, etc.'},
                    'metadata': {'step': 5, 'total_steps': 7}
                }
            
            # Standard referral source selected
            self.session_manager.update_session(session_id, 'demo_awaiting_date', {'referral_source': referral_source})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': "Great! 👍\n\nWhat's your preferred date and time?",
                'rich_payload': {'input_type': 'datetime', 'placeholder': 'e.g., 12-11-25, 4:00 PM'},
                'metadata': {'step': 6, 'total_steps': 7}
            }
        
        # Step 6b: Collect custom referral source (when "Other" was selected)
        elif current_state == 'demo_awaiting_custom_referral':
            custom_referral = query.strip()
            self.session_manager.update_session(session_id, 'demo_awaiting_date', {'referral_source': custom_referral})
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': "Perfect! 👍\n\nWhat's your preferred date and time?",
                'rich_payload': {'input_type': 'datetime', 'placeholder': 'e.g., 12-11-25, 4:00 PM'},
                'metadata': {'step': 6, 'total_steps': 7}
            }
        
        # Step 7: Complete flow
        elif current_state == 'demo_awaiting_date':
            preferred_date = query.strip()
            session_data = session['data']
            session_data['preferred_date'] = preferred_date
            
            # Generate ticket ID
            ticket_id = str(uuid.uuid4())[:8].upper()
            
            # Save lead to database
            if DATABASE_ENABLED:
                lead_data = database_service.format_demo_lead(session_data, ticket_id)
                database_service.save_lead(lead_data)
            
            # Clear session state
            self.session_manager.clear_session_state(session_id)
            
            # Format confirmation
            confirmation = f"""✅ **Demo Confirmed!**

**Your Details:**
- Industry: {session_data.get('industry', 'N/A')}
- Name: {session_data.get('name', 'N/A')}
- Email: {session_data.get('email', 'N/A')}
- Phone: {session_data.get('phone', 'N/A')}
- Referral: {session_data.get('referral_source', 'N/A')}
- Date: {preferred_date}
- Ticket ID: **{ticket_id}**

Our team will contact you shortly! 🚀"""
            
            return {
                'type': 'transaction',
                'flow': 'demo',
                'response': confirmation,
                'action': 'demo_confirmed',
                'ticket_id': ticket_id,
                'demo_data': session_data,
                'rich_payload': {
                    'buttons': [
                        {'label': '📋 View Services', 'action': 'open_link', 'url': 'https://www.instalogic.in/our-services/'},
                        {'label': '📚 Case Studies', 'action': 'open_link', 'url': 'https://www.instalogic.in/case-studies/'}
                    ]
                },
                'metadata': {'step': 7, 'total_steps': 7, 'completed': True}
            }
        
        # Fallback
        return {
            'type': 'error',
            'response': "I'm sorry, something went wrong with the demo request. Let's start over. Would you like to request a demo?",
            'rich_payload': {
                'buttons': [
                    {'label': '🎯 Start Demo Request', 'action': 'start_demo_flow'},
                    {'label': '❌ Cancel', 'action': 'cancel_flow'}
                ]
            }
        }
    
    def handle_career_flow(self, query: str, session_id: str) -> Dict:
        """Multi-turn career application flow"""
        session = self.session_manager.get_session(session_id)
        current_state = session['state']
        
        if current_state is None:
            self.session_manager.update_session(session_id, 'career_awaiting_name', {})
            return {
                'type': 'transaction',
                'flow': 'career',
                'response': "Excited to hear you're interested in joining InstaLogic! 💼\n\nLet me collect some information. What's your full name?",
                'rich_payload': {'input_type': 'text'},
                'metadata': {'step': 1, 'total_steps': 4}
            }
        
        elif current_state == 'career_awaiting_name':
            name = query.strip()
            self.session_manager.update_session(session_id, 'career_awaiting_email', {'name': name})
            return {
                'type': 'transaction',
                'flow': 'career',
                'response': f"Great, **{name}**! What's your email address?",
                'rich_payload': {'input_type': 'email'},
                'metadata': {'step': 2, 'total_steps': 4}
            }
        
        elif current_state == 'career_awaiting_email':
            email = query.strip()
            self.session_manager.update_session(session_id, 'career_awaiting_position', {'email': email})
            return {
                'type': 'transaction',
                'flow': 'career',
                'response': "Which position are you interested in?",
                'rich_payload': {
                    'buttons': [
                        {'label': 'Data Analyst', 'action': 'select_position', 'value': 'Data Analyst'},
                        {'label': 'Software Engineer', 'action': 'select_position', 'value': 'Software Engineer'},
                        {'label': 'BI Consultant', 'action': 'select_position', 'value': 'BI Consultant'},
                        {'label': 'Other', 'action': 'select_position', 'value': 'Other'}
                    ]
                },
                'metadata': {'step': 3, 'total_steps': 4}
            }
        
        elif current_state == 'career_awaiting_position':
            position = query.strip()
            session_data = session['data']
            session_data['position'] = position
            
            ticket_id = str(uuid.uuid4())[:8].upper()
            
            # Save career lead to database
            if DATABASE_ENABLED:
                lead_data = database_service.format_career_lead(session_data, ticket_id)
                database_service.save_lead(lead_data)
            
            self.session_manager.clear_session_state(session_id)
            
            return {
                'type': 'transaction',
                'flow': 'career',
                'response': f"✅ **Application Received!**\n\nThank you for your interest in the **{position}** position. Your application ID is **{ticket_id}**.\n\nPlease email your resume to careers@instalogic.in with this ID in the subject line.",
                'action': 'career_submitted',
                'ticket_id': ticket_id,
                'career_data': session_data,
                'rich_payload': {
                    'buttons': [
                        {'label': '📄 Upload Resume', 'action': 'show_resume_form'},
                        {'label': '💼 View Careers Page', 'action': 'open_link', 'url': 'https://www.instalogic.in/careers/'}
                    ]
                },
                'metadata': {'step': 4, 'total_steps': 4, 'completed': True}
            }
    
    def handle_rfp_flow(self, query: str, session_id: str) -> Dict:
        """Multi-turn RFP upload flow"""
        session = self.session_manager.get_session(session_id)
        current_state = session['state']
        
        if current_state is None:
            self.session_manager.update_session(session_id, 'rfp_awaiting_company', {})
            return {
                'type': 'transaction',
                'flow': 'rfp',
                'response': "Thank you for considering InstaLogic for your project! 📤\n\nWhat's your company name?",
                'rich_payload': {'input_type': 'text'},
                'metadata': {'step': 1, 'total_steps': 4}
            }
        
        elif current_state == 'rfp_awaiting_company':
            company = query.strip()
            self.session_manager.update_session(session_id, 'rfp_awaiting_contact', {'company': company})
            return {
                'type': 'transaction',
                'flow': 'rfp',
                'response': "What's the best email to reach you at?",
                'rich_payload': {'input_type': 'email'},
                'metadata': {'step': 2, 'total_steps': 4}
            }
        
        elif current_state == 'rfp_awaiting_contact':
            email = query.strip()
            self.session_manager.update_session(session_id, 'rfp_awaiting_brief', {'email': email})
            return {
                'type': 'transaction',
                'flow': 'rfp',
                'response': "Please provide a brief description of your project:",
                'rich_payload': {'input_type': 'textarea', 'placeholder': 'Project requirements, timeline, budget range...'},
                'metadata': {'step': 3, 'total_steps': 4}
            }
        
        elif current_state == 'rfp_awaiting_brief':
            brief = query.strip()
            session_data = session['data']
            session_data['brief'] = brief
            
            ticket_id = str(uuid.uuid4())[:8].upper()
            
            # Save RFP lead to database
            if DATABASE_ENABLED:
                lead_data = database_service.format_rfp_lead(session_data, ticket_id)
                database_service.save_lead(lead_data)
            
            self.session_manager.clear_session_state(session_id)
            
            return {
                'type': 'transaction',
                'flow': 'rfp',
                'response': f"✅ **RFP Received!**\n\nYour RFP has been submitted successfully. Reference ID: **{ticket_id}**\n\nOur proposals team will review it and respond within 24-48 hours. You can also email your detailed RFP document to proposals@instalogic.in",
                'action': 'rfp_submitted',
                'ticket_id': ticket_id,
                'rfp_data': session_data,
                'rich_payload': {
                    'buttons': [
                        {'label': '📧 Email RFP Document', 'action': 'open_email', 'value': 'proposals@instalogic.in'},
                        {'label': '📞 Schedule Call', 'action': 'start_contact_flow'}
                    ]
                },
                'metadata': {'step': 4, 'total_steps': 4, 'completed': True}
            }
    
    def handle_contact_flow(self, query: str, session_id: str) -> Dict:
        """Multi-turn contact request flow"""
        session = self.session_manager.get_session(session_id)
        current_state = session['state']
        
        if current_state is None:
            self.session_manager.update_session(session_id, 'contact_awaiting_name', {})
            return {
                'type': 'transaction',
                'flow': 'contact',
                'response': "I'll help you get in touch with our team! 📞\n\nWhat's your name?",
                'rich_payload': {'input_type': 'text'},
                'metadata': {'step': 1, 'total_steps': 3}
            }
        
        elif current_state == 'contact_awaiting_name':
            name = query.strip()
            self.session_manager.update_session(session_id, 'contact_awaiting_method', {'name': name})
            return {
                'type': 'transaction',
                'flow': 'contact',
                'response': f"Thanks, **{name}**! How would you prefer to be contacted?",
                'rich_payload': {
                    'buttons': [
                        {'label': '📧 Email', 'action': 'select_contact_method', 'value': 'email'},
                        {'label': '📞 Phone', 'action': 'select_contact_method', 'value': 'phone'},
                        {'label': '💬 Both', 'action': 'select_contact_method', 'value': 'both'}
                    ]
                },
                'metadata': {'step': 2, 'total_steps': 3}
            }
        
        elif current_state == 'contact_awaiting_method':
            method = query.strip().lower()
            session_data = session['data']
            ticket_id = str(uuid.uuid4())[:8].upper()
            self.session_manager.clear_session_state(session_id)
            
            contact_info = {
                'email': '📧 info@instalogic.in',
                'phone': '📞 +91-XXX-XXX-XXXX',
                'both': '📧 info@instalogic.in\n📞 +91-XXX-XXX-XXXX'
            }.get(method, '📧 info@instalogic.in')
            
            return {
                'type': 'transaction',
                'flow': 'contact',
                'response': f"✅ **Contact Request Received!**\n\nReference ID: **{ticket_id}**\n\nYou can also reach us directly at:\n{contact_info}",
                'action': 'contact_submitted',
                'ticket_id': ticket_id,
                'contact_data': session_data,
                'rich_payload': {
                    'buttons': [
                        {'label': '🌐 Visit Website', 'action': 'open_link', 'url': 'https://www.instalogic.in/contact-us/'},
                        {'label': '📋 View Services', 'action': 'open_link', 'url': 'https://www.instalogic.in/our-services/'}
                    ]
                },
                'metadata': {'step': 3, 'total_steps': 3, 'completed': True}
            }


# Initialize the orchestrator
def create_orchestrator(bedrock_client: BedrockClient) -> ChatbotOrchestrator:
    """Factory function to create orchestrator instance"""
    return ChatbotOrchestrator(bedrock_client)
