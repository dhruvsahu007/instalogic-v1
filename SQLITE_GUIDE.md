# SQLite Lead Management System - Quick Start Guide

## Overview

Your chatbot now uses **SQLite** for lead management instead of Firebase. SQLite is a lightweight, file-based database that requires zero configuration and no external services.

## 🎯 Key Benefits

- ✅ **Zero Setup** - No API keys, credentials, or cloud services needed
- ✅ **Local Storage** - All data stored in a single file (`chatbot_leads.db`)
- ✅ **Fast & Simple** - No network latency, instant queries
- ✅ **Built-in** - SQLite comes with Python (no installation needed)
- ✅ **Portable** - Easy to backup, migrate, or version control

---

## 🚀 Quick Start (5 minutes)

### Step 1: Verify Database Service

The database service has already been created at:
```
backend/database_service.py
```

This file contains:
- `DatabaseService` class with all database operations
- Auto-initialization of tables on first run
- Format helpers for different lead types
- Full CRUD operations

### Step 2: Run the Backend

```bash
cd backend
python main.py
```

The database file `chatbot_leads.db` will be automatically created in the backend directory on first run.

### Step 3: Test Lead Saving

Interact with your chatbot using any transactional flow:
- Request a demo
- Ask for human assistance
- Submit a career application
- Upload an RFP

You'll see console output:
```
✅ SQLite database initialized: chatbot_leads.db
✅ Database tables initialized
✅ Lead saved to database: ID 1
```

### Step 4: View Leads in Dashboard

Start your frontend:
```bash
cd frontend
npm run dev
```

Navigate to the leads dashboard component (replace the old Firebase dashboard with the new `LeadsDashboard.jsx`).

---

## 📊 Database Schema

### `chatbot_leads` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `type` | TEXT | Lead type: DEMO_REQUEST, HUMAN_HANDOFF, RFP_UPLOAD, CAREER_APPLICATION |
| `name` | TEXT | Contact name |
| `contact` | TEXT | Email or phone |
| `info` | TEXT | Additional details about the request |
| `status` | TEXT | NEW, CONTACTED, IN_PROGRESS, CLOSED |
| `admin_notes` | TEXT | Notes added by admin |
| `requested_date` | TIMESTAMP | When the lead was created |
| `ticket_id` | TEXT | Unique ticket identifier |
| `metadata` | TEXT | JSON string with additional data |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

---

## 🔧 API Endpoints

### Get All Leads
```http
GET /api/leads
GET /api/leads?status=NEW
```

**Response:**
```json
{
  "success": true,
  "leads": [
    {
      "id": 1,
      "type": "DEMO_REQUEST",
      "name": "John Doe",
      "contact": "john@example.com",
      "info": "Industry: Healthcare. Preferred Date: 2024-12-15",
      "status": "NEW",
      "adminNotes": "",
      "requestedDate": "2024-12-01 10:30:00",
      "ticketId": "ABC123",
      "metadata": {...}
    }
  ],
  "count": 1
}
```

### Get Single Lead
```http
GET /api/leads/{lead_id}
```

### Update Lead Status
```http
PUT /api/leads/{lead_id}/status?status=CONTACTED
```

Valid statuses: `NEW`, `CONTACTED`, `IN_PROGRESS`, `CLOSED`

### Update Admin Notes
```http
PUT /api/leads/{lead_id}/notes?notes=Called%20customer%20today
```

### Delete Lead
```http
DELETE /api/leads/{lead_id}
```

### Get Statistics
```http
GET /api/leads/statistics
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total": 25,
    "by_status": {
      "NEW": 10,
      "CONTACTED": 8,
      "IN_PROGRESS": 5,
      "CLOSED": 2
    },
    "by_type": {
      "DEMO_REQUEST": 12,
      "HUMAN_HANDOFF": 6,
      "RFP_UPLOAD": 4,
      "CAREER_APPLICATION": 3
    }
  }
}
```

---

## 💾 Database Operations

### Saving a Lead (Backend)

```python
from database_service import database_service

# Format the lead data
lead_data = database_service.format_demo_lead(
    demo_data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'industry': 'Healthcare',
        'preferred_date': '2024-12-15'
    },
    ticket_id='ABC123'
)

# Save to database
lead_id = database_service.save_lead(lead_data)
```

### Querying Leads

```python
# Get all leads
all_leads = database_service.get_all_leads()

# Get leads by status
new_leads = database_service.get_all_leads(status='NEW')

# Get single lead
lead = database_service.get_lead_by_id(1)

# Get statistics
stats = database_service.get_statistics()
```

### Updating Leads

```python
# Update status
database_service.update_lead_status(lead_id=1, new_status='CONTACTED')

# Update notes
database_service.update_lead_notes(lead_id=1, notes='Customer very interested')
```

### Deleting Leads

```python
database_service.delete_lead(lead_id=1)
```

---

## 🖥️ Frontend Integration

### Using the New Dashboard

Replace your Firebase dashboard import with:

```jsx
import LeadsDashboard from './components/LeadsDashboard';

function App() {
  return (
    <div>
      <LeadsDashboard />
    </div>
  );
}
```

### Dashboard Features

✅ **Real-time Auto-Refresh** - Updates every 30 seconds  
✅ **Status Filtering** - Filter by ALL, NEW, CONTACTED, IN_PROGRESS, CLOSED  
✅ **Statistics Cards** - View total leads and breakdown by status  
✅ **Status Workflow** - One-click status progression  
✅ **Admin Notes** - Edit and save notes inline  
✅ **Delete Leads** - Remove leads with confirmation  
✅ **Responsive Design** - Works on desktop and mobile  

---

## 🔍 Viewing Database Contents

### Option 1: SQLite Command Line

```bash
cd backend
sqlite3 chatbot_leads.db

# List tables
.tables

# View all leads
SELECT * FROM chatbot_leads;

# View recent leads
SELECT id, type, name, status, requested_date 
FROM chatbot_leads 
ORDER BY requested_date DESC 
LIMIT 10;

# Count by status
SELECT status, COUNT(*) as count 
FROM chatbot_leads 
GROUP BY status;

# Exit
.quit
```

### Option 2: DB Browser for SQLite (GUI)

1. Download from: https://sqlitebrowser.org/
2. Open `backend/chatbot_leads.db`
3. Browse data, run queries, edit records

### Option 3: Python Script

```python
import sqlite3

conn = sqlite3.connect('chatbot_leads.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM chatbot_leads ORDER BY requested_date DESC LIMIT 10')
leads = cursor.fetchall()

for lead in leads:
    print(f"ID: {lead['id']}, Name: {lead['name']}, Status: {lead['status']}")

conn.close()
```

---

## 📦 Backup & Migration

### Backup Database

```bash
# Simple copy
cp chatbot_leads.db chatbot_leads_backup_$(date +%Y%m%d).db

# With compression
tar -czf chatbot_leads_backup_$(date +%Y%m%d).tar.gz chatbot_leads.db
```

### Export to CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('chatbot_leads.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM chatbot_leads')
leads = cursor.fetchall()

with open('leads_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])  # Headers
    writer.writerows(leads)

conn.close()
```

### Migrate to Another Database

If you later want to move to PostgreSQL or MySQL:

1. Export data to CSV (above)
2. Create new database schema
3. Import CSV data
4. Update `database_service.py` connection string

---

## 🛠️ Configuration

### Change Database Location

In `.env` file:
```env
DATABASE_PATH=./data/leads.db
```

Or when initializing:
```python
from database_service import DatabaseService

db = DatabaseService(db_path='/custom/path/leads.db')
```

### Database Optimization

For production, add these SQLite settings:

```python
# In database_service.py, update get_connection():
conn = sqlite3.connect(self.db_path)
conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
conn.execute('PRAGMA synchronous=NORMAL')  # Faster writes
conn.execute('PRAGMA cache_size=-64000')  # 64MB cache
conn.row_factory = sqlite3.Row
```

---

## 🐛 Troubleshooting

### Issue: Database file not found

**Solution:** The database is auto-created on first run. Just start the backend.

### Issue: Database locked

**Solution:** Another process is accessing the database. Close other connections or enable WAL mode:
```python
conn.execute('PRAGMA journal_mode=WAL')
```

### Issue: Old leads not appearing

**Solution:** Check filter status. Click "ALL" to see all leads regardless of status.

### Issue: Permission denied

**Solution:** Ensure the backend directory is writable:
```bash
chmod 755 backend/
```

---

## 📈 Performance

SQLite can handle:
- ✅ Thousands of leads with no performance issues
- ✅ Multiple concurrent reads
- ✅ Single writer at a time (sufficient for chatbot use case)
- ✅ Up to 281 terabytes database size (you're safe 😄)

For higher concurrency (multiple admins editing simultaneously), consider:
- Enable WAL mode (Write-Ahead Logging)
- Or migrate to PostgreSQL/MySQL

---

## 🎓 Next Steps

1. **Customize the Schema** - Add fields specific to your business
2. **Add Email Notifications** - Send alerts when new leads arrive
3. **Export Reports** - Generate weekly/monthly lead reports
4. **Integrate CRM** - Sync leads to Salesforce, HubSpot, etc.
5. **Add Search** - Full-text search across lead details
6. **Lead Scoring** - Automatically prioritize high-value leads

---

## 📚 Resources

- [SQLite Documentation](https://sqlite.org/docs.html)
- [Python sqlite3 Module](https://docs.python.org/3/library/sqlite3.html)
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite Performance Tips](https://www.sqlite.org/speed.html)

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] Database file created (`chatbot_leads.db`)
- [ ] Console shows "✅ Lead saved to database" when testing flows
- [ ] Dashboard displays leads
- [ ] Filtering works (NEW, CONTACTED, etc.)
- [ ] Status updates work
- [ ] Admin notes can be saved
- [ ] Statistics show correct counts

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the console for error messages
2. Verify the database file exists: `ls -la backend/chatbot_leads.db`
3. Test with SQLite command line: `sqlite3 backend/chatbot_leads.db "SELECT COUNT(*) FROM chatbot_leads;"`
4. Check API health: `curl http://localhost:8000/api/leads`

---

**Congratulations!** Your chatbot now has a simple, reliable, zero-config lead management system with SQLite. 🎉
