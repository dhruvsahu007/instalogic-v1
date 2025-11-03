"""
SQLite Database Service for saving chatbot leads
"""
import os
import sqlite3
import json
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


class DatabaseService:
    """Service for managing SQLite database operations"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'chatbot_leads.db')
        
        self.db_path = db_path
        self.init_database()
        print(f"✅ SQLite database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create leads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chatbot_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    info TEXT,
                    status TEXT DEFAULT 'NEW',
                    admin_notes TEXT DEFAULT '',
                    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ticket_id TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON chatbot_leads(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_type 
                ON chatbot_leads(type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requested_date 
                ON chatbot_leads(requested_date DESC)
            ''')
            
            print("✅ Database tables initialized")
    
    def save_lead(self, lead_data: Dict) -> Optional[int]:
        """
        Save lead data to SQLite database
        
        Args:
            lead_data: Dictionary containing lead information
                {
                    "type": "DEMO_REQUEST" | "HUMAN_HANDOFF" | "RFP_UPLOAD" | "CAREER_APPLICATION",
                    "name": str,
                    "contact": str (email or phone),
                    "info": str (details about the request),
                    "metadata": dict (additional data)
                }
        
        Returns:
            Lead ID if successful, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare the data
                metadata_json = json.dumps(lead_data.get('metadata', {}))
                
                cursor.execute('''
                    INSERT INTO chatbot_leads 
                    (type, name, contact, info, status, admin_notes, ticket_id, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lead_data.get('type', 'UNKNOWN'),
                    lead_data.get('name', 'N/A'),
                    lead_data.get('contact', 'N/A'),
                    lead_data.get('info', ''),
                    'NEW',
                    '',
                    lead_data.get('ticket_id', ''),
                    metadata_json
                ))
                
                lead_id = cursor.lastrowid
                print(f"✅ Lead saved to database: ID {lead_id}")
                return lead_id
                
        except Exception as e:
            print(f"❌ Error saving lead to database: {str(e)}")
            return None
    
    def get_all_leads(self, status: str = None) -> List[Dict]:
        """Get all leads, optionally filtered by status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if status and status != 'ALL':
                    cursor.execute('''
                        SELECT * FROM chatbot_leads 
                        WHERE status = ?
                        ORDER BY requested_date DESC
                    ''', (status,))
                else:
                    cursor.execute('''
                        SELECT * FROM chatbot_leads 
                        ORDER BY requested_date DESC
                    ''')
                
                rows = cursor.fetchall()
                leads = []
                
                for row in rows:
                    lead = {
                        'id': row['id'],
                        'type': row['type'],
                        'name': row['name'],
                        'contact': row['contact'],
                        'info': row['info'],
                        'status': row['status'],
                        'adminNotes': row['admin_notes'],
                        'requestedDate': row['requested_date'],
                        'ticketId': row['ticket_id'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'createdAt': row['created_at'],
                        'updatedAt': row['updated_at']
                    }
                    leads.append(lead)
                
                return leads
                
        except Exception as e:
            print(f"❌ Error fetching leads: {str(e)}")
            return []
    
    def update_lead_status(self, lead_id: int, new_status: str) -> bool:
        """Update lead status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE chatbot_leads 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_status, lead_id))
                
                if cursor.rowcount > 0:
                    print(f"✅ Updated lead {lead_id} status to {new_status}")
                    return True
                else:
                    print(f"⚠️  Lead {lead_id} not found")
                    return False
                    
        except Exception as e:
            print(f"❌ Error updating lead status: {str(e)}")
            return False
    
    def update_lead_notes(self, lead_id: int, notes: str) -> bool:
        """Update admin notes for a lead"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE chatbot_leads 
                    SET admin_notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (notes, lead_id))
                
                if cursor.rowcount > 0:
                    print(f"✅ Updated lead {lead_id} notes")
                    return True
                else:
                    print(f"⚠️  Lead {lead_id} not found")
                    return False
                    
        except Exception as e:
            print(f"❌ Error updating lead notes: {str(e)}")
            return False
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Dict]:
        """Get a specific lead by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM chatbot_leads WHERE id = ?
                ''', (lead_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row['id'],
                        'type': row['type'],
                        'name': row['name'],
                        'contact': row['contact'],
                        'info': row['info'],
                        'status': row['status'],
                        'adminNotes': row['admin_notes'],
                        'requestedDate': row['requested_date'],
                        'ticketId': row['ticket_id'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'createdAt': row['created_at'],
                        'updatedAt': row['updated_at']
                    }
                return None
                
        except Exception as e:
            print(f"❌ Error fetching lead: {str(e)}")
            return None
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead (use with caution)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM chatbot_leads WHERE id = ?
                ''', (lead_id,))
                
                if cursor.rowcount > 0:
                    print(f"✅ Deleted lead {lead_id}")
                    return True
                else:
                    print(f"⚠️  Lead {lead_id} not found")
                    return False
                    
        except Exception as e:
            print(f"❌ Error deleting lead: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get lead statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total leads
                cursor.execute('SELECT COUNT(*) as count FROM chatbot_leads')
                total = cursor.fetchone()['count']
                
                # Leads by status
                cursor.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM chatbot_leads 
                    GROUP BY status
                ''')
                status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # Leads by type
                cursor.execute('''
                    SELECT type, COUNT(*) as count 
                    FROM chatbot_leads 
                    GROUP BY type
                ''')
                type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total': total,
                    'by_status': status_counts,
                    'by_type': type_counts
                }
                
        except Exception as e:
            print(f"❌ Error fetching statistics: {str(e)}")
            return {'total': 0, 'by_status': {}, 'by_type': {}}
    
    def format_demo_lead(self, demo_data: Dict, ticket_id: str) -> Dict:
        """Format demo request data for database"""
        return {
            'type': 'DEMO_REQUEST',
            'name': demo_data.get('name', 'N/A'),
            'contact': f"{demo_data.get('email', 'N/A')} | {demo_data.get('phone', 'N/A')}",
            'info': f"Industry: {demo_data.get('industry', 'N/A')}. Date: {demo_data.get('preferred_date', 'N/A')}. Referral: {demo_data.get('referral_source', 'N/A')}",
            'ticket_id': ticket_id,
            'metadata': {
                'industry': demo_data.get('industry'),
                'email': demo_data.get('email'),
                'phone': demo_data.get('phone'),
                'referral_source': demo_data.get('referral_source'),
                'preferred_date': demo_data.get('preferred_date')
            }
        }
    
    def format_handoff_lead(self, query: str, ticket_id: str) -> Dict:
        """Format human handoff data for database"""
        return {
            'type': 'HUMAN_HANDOFF',
            'name': 'Urgent Request',
            'contact': 'See chat history',
            'info': f"User requested human assistance: {query}",
            'ticket_id': ticket_id,
            'metadata': {
                'original_query': query,
                'priority': 'high'
            }
        }
    
    def format_rfp_lead(self, rfp_data: Dict, ticket_id: str) -> Dict:
        """Format RFP upload data for database"""
        return {
            'type': 'RFP_UPLOAD',
            'name': 'RFP Submission',
            'contact': rfp_data.get('email', 'N/A'),
            'info': f"Company: {rfp_data.get('company', 'N/A')}. Brief: {rfp_data.get('brief', 'N/A')}",
            'ticket_id': ticket_id,
            'metadata': {
                'company': rfp_data.get('company'),
                'email': rfp_data.get('email'),
                'brief': rfp_data.get('brief')
            }
        }
    
    def format_career_lead(self, career_data: Dict, ticket_id: str) -> Dict:
        """Format career application data for database"""
        return {
            'type': 'CAREER_APPLICATION',
            'name': career_data.get('name', 'N/A'),
            'contact': career_data.get('email', 'N/A'),
            'info': f"Position: {career_data.get('position', 'N/A')}",
            'ticket_id': ticket_id,
            'metadata': {
                'position': career_data.get('position'),
                'email': career_data.get('email')
            }
        }


# Create singleton instance
database_service = DatabaseService()


def save_lead_to_database(lead_data: Dict) -> Optional[int]:
    """
    Convenience function to save lead data
    
    Usage:
        from database_service import save_lead_to_database
        
        lead_data = {
            'type': 'DEMO_REQUEST',
            'name': 'John Doe',
            'contact': 'john@example.com',
            'info': 'Looking for a demo',
            'ticket_id': 'ABC123'
        }
        
        lead_id = save_lead_to_database(lead_data)
    """
    return database_service.save_lead(lead_data)

