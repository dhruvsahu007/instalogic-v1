"""
Universal Database Service - Supports both SQLite and PostgreSQL
"""
import os
import json
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

# Determine database type
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite').lower()

if DATABASE_TYPE == 'postgresql':
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRESQL = True
else:
    import sqlite3
    USE_POSTGRESQL = False


class DatabaseService:
    """Service for managing database operations (SQLite or PostgreSQL)"""
    
    def __init__(self, db_path: str = None):
        self.use_postgresql = USE_POSTGRESQL
        
        if self.use_postgresql:
            # PostgreSQL configuration
            self.pg_config = {
                'host': os.getenv('RDS_HOST'),
                'port': int(os.getenv('RDS_PORT', 5432)),
                'database': os.getenv('RDS_DATABASE', 'postgres'),
                'user': os.getenv('RDS_USERNAME'),
                'password': os.getenv('RDS_PASSWORD')
            }
            print(f"[INFO] PostgreSQL database initialized: {self.pg_config['host']}")
        else:
            # SQLite configuration
            if db_path is None:
                db_path = os.getenv('DATABASE_PATH', 'chatbot_leads.db')
            self.db_path = db_path
            print(f"[INFO] SQLite database initialized: {self.db_path}")
        
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self.use_postgresql:
            conn = psycopg2.connect(**self.pg_config)
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
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
            
            if self.use_postgresql:
                # PostgreSQL table creation
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chatbot_leads (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(50) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        contact TEXT NOT NULL,
                        info TEXT,
                        status VARCHAR(50) DEFAULT 'NEW',
                        admin_notes TEXT DEFAULT '',
                        requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ticket_id VARCHAR(50),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
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
            else:
                # SQLite table creation
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
                
                # Create indexes
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
            
            print("[INFO] Database tables initialized")
    
    def save_lead(self, lead_data: Dict) -> Optional[int]:
        """Save lead data to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare metadata
                metadata = lead_data.get('metadata', {})
                if self.use_postgresql:
                    metadata_str = json.dumps(metadata) if metadata else '{}'
                else:
                    metadata_str = json.dumps(metadata) if metadata else '{}'
                
                # Insert query
                if self.use_postgresql:
                    cursor.execute('''
                        INSERT INTO chatbot_leads 
                        (type, name, contact, info, ticket_id, metadata, requested_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (
                        lead_data.get('type'),
                        lead_data.get('name'),
                        lead_data.get('contact'),
                        lead_data.get('info'),
                        lead_data.get('ticket_id'),
                        metadata_str,
                        lead_data.get('requested_date', datetime.now())
                    ))
                    lead_id = cursor.fetchone()[0]
                else:
                    cursor.execute('''
                        INSERT INTO chatbot_leads 
                        (type, name, contact, info, ticket_id, metadata, requested_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lead_data.get('type'),
                        lead_data.get('name'),
                        lead_data.get('contact'),
                        lead_data.get('info'),
                        lead_data.get('ticket_id'),
                        metadata_str,
                        lead_data.get('requested_date', datetime.now().isoformat())
                    ))
                    lead_id = cursor.lastrowid
                
                print(f"[INFO] Lead saved successfully (ID: {lead_id})")
                return lead_id
                
        except Exception as e:
            print(f"[ERROR] Failed to save lead: {e}")
            return None
    
    def get_all_leads(self, status: Optional[str] = None) -> List[Dict]:
        """Get all leads, optionally filtered by status"""
        try:
            with self.get_connection() as conn:
                if self.use_postgresql:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                else:
                    cursor = conn.cursor()
                
                if status:
                    if self.use_postgresql:
                        cursor.execute('''
                            SELECT * FROM chatbot_leads 
                            WHERE status = %s 
                            ORDER BY created_at DESC
                        ''', (status,))
                    else:
                        cursor.execute('''
                            SELECT * FROM chatbot_leads 
                            WHERE status = ? 
                            ORDER BY created_at DESC
                        ''', (status,))
                else:
                    cursor.execute('''
                        SELECT * FROM chatbot_leads 
                        ORDER BY created_at DESC
                    ''')
                
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                leads = []
                for row in rows:
                    if self.use_postgresql:
                        lead = dict(row)
                        # Parse JSONB metadata
                        if isinstance(lead.get('metadata'), str):
                            try:
                                lead['metadata'] = json.loads(lead['metadata'])
                            except:
                                lead['metadata'] = {}
                    else:
                        lead = dict(row)
                        # Parse JSON metadata
                        if lead.get('metadata'):
                            try:
                                lead['metadata'] = json.loads(lead['metadata'])
                            except:
                                lead['metadata'] = {}
                    
                    # Convert datetime to ISO format
                    for key in ['created_at', 'updated_at', 'requested_date']:
                        if key in lead and lead[key]:
                            if isinstance(lead[key], datetime):
                                lead[key] = lead[key].isoformat()
                    
                    leads.append(lead)
                
                return leads
                
        except Exception as e:
            print(f"[ERROR] Failed to get leads: {e}")
            return []
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Dict]:
        """Get a specific lead by ID"""
        try:
            with self.get_connection() as conn:
                if self.use_postgresql:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute('SELECT * FROM chatbot_leads WHERE id = %s', (lead_id,))
                else:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM chatbot_leads WHERE id = ?', (lead_id,))
                
                row = cursor.fetchone()
                if row:
                    lead = dict(row)
                    # Parse metadata
                    if lead.get('metadata'):
                        try:
                            if isinstance(lead['metadata'], str):
                                lead['metadata'] = json.loads(lead['metadata'])
                        except:
                            lead['metadata'] = {}
                    return lead
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to get lead: {e}")
            return None
    
    def update_lead_status(self, lead_id: int, status: str) -> bool:
        """Update lead status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if self.use_postgresql:
                    cursor.execute('''
                        UPDATE chatbot_leads 
                        SET status = %s, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    ''', (status, lead_id))
                else:
                    cursor.execute('''
                        UPDATE chatbot_leads 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (status, lead_id))
                
                # Check if any rows were affected
                rows_affected = cursor.rowcount
                return rows_affected > 0
        except Exception as e:
            print(f"[ERROR] Failed to update status: {e}")
            return False
    
    def update_lead_notes(self, lead_id: int, notes: str) -> bool:
        """Update admin notes for a lead"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if self.use_postgresql:
                    cursor.execute('''
                        UPDATE chatbot_leads 
                        SET admin_notes = %s, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    ''', (notes, lead_id))
                else:
                    cursor.execute('''
                        UPDATE chatbot_leads 
                        SET admin_notes = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (notes, lead_id))
                
                # Check if any rows were affected
                rows_affected = cursor.rowcount
                return rows_affected > 0
        except Exception as e:
            print(f"[ERROR] Failed to update notes: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get lead statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total leads
                cursor.execute('SELECT COUNT(*) FROM chatbot_leads')
                stats['total'] = cursor.fetchone()[0]
                
                # By status
                if self.use_postgresql:
                    cursor.execute('SELECT status, COUNT(*) FROM chatbot_leads GROUP BY status')
                else:
                    cursor.execute('SELECT status, COUNT(*) FROM chatbot_leads GROUP BY status')
                
                for row in cursor.fetchall():
                    stats[row[0].lower()] = row[1]
                
                return stats
                
        except Exception as e:
            print(f"[ERROR] Failed to get statistics: {e}")
            return {}
    
    # Format helper methods
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
            'name': 'Escalated User',
            'contact': 'Via Chat',
            'info': f"User request: {query}",
            'ticket_id': ticket_id,
            'metadata': {
                'query': query,
                'priority': 'high'
            }
        }


# Create singleton instance
database_service = DatabaseService()

