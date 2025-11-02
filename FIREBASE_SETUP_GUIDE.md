# Firebase Admin Dashboard Setup Guide

## 🔥 Complete Firebase Integration for Chat Leads

This guide covers the complete setup for saving chatbot leads to Firebase Firestore and viewing them in a real-time admin dashboard.

---

## 📦 Part 1: Backend Setup (Python)

### 1.1 Install Firebase Admin SDK

```bash
cd backend
pip install firebase-admin
```

### 1.2 Get Firebase Credentials

**Option A: Service Account (Recommended for Production)**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click ⚙️ Settings → Project Settings
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file
7. Save it as `backend/firebase-credentials.json`

**Option B: Default Credentials (For Google Cloud)**

If running on Google Cloud (App Engine, Cloud Run, etc.), you can use default credentials without a file.

### 1.3 Configure Environment Variables

Add to `backend/.env`:

```bash
# Firebase Configuration
FIREBASE_APP_ID=instalogic-chatbot
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### 1.4 Files Created

✅ **`firebase_service.py`** - Firebase service class
✅ **`chatbot_orchestrator.py`** - Updated with Firebase integration

### 1.5 How It Works

When a guided flow completes:

```python
# Demo Request Flow
demo_data = {'name': 'John Doe', 'email': 'john@example.com', ...}
ticket_id = 'ABC123XY'

# Automatically saved to Firestore
lead_data = firebase_service.format_demo_lead(demo_data, ticket_id)
firebase_service.save_lead_to_firestore(lead_data)
```

**Firestore Document Structure:**

```json
{
  "type": "DEMO_REQUEST",
  "name": "John Doe",
  "contact": "john@example.com",
  "info": "Industry: Finance. Preferred Date: Next Monday",
  "status": "NEW",
  "adminNotes": "",
  "requestedDate": "2025-11-03T10:30:00Z",
  "ticketId": "ABC123XY",
  "metadata": {
    "industry": "Finance",
    "email": "john@example.com",
    "preferred_date": "Next Monday"
  }
}
```

**Collection Path:**
```
/artifacts/{appId}/public/data/chatbot_leads/{docId}
```

---

## 🎨 Part 2: Frontend Admin Dashboard

### 2.1 Install Firebase SDK

```bash
cd frontend
npm install firebase
```

### 2.2 Component Created

✅ **`ChatResponsesDashboard.jsx`** - Complete admin dashboard

### 2.3 Add Dashboard Route

**Option A: Add to existing App.jsx:**

```jsx
// frontend/src/App.jsx
import ChatResponsesDashboard from './components/ChatResponsesDashboard';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/admin/leads" element={<ChatResponsesDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Option B: Standalone Page:**

Create `frontend/admin.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>InstaLogic - Lead Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/admin.jsx"></script>
</body>
</html>
```

Create `frontend/src/admin.jsx`:

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import ChatResponsesDashboard from './components/ChatResponsesDashboard';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ChatResponsesDashboard />
  </React.StrictMode>
);
```

### 2.4 Configure Firebase (Frontend)

**Set Global Variables:**

In your HTML or before rendering the dashboard:

```html
<script>
  // Firebase configuration
  window.__firebase_config = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
  };
  
  window.__app_id = "instalogic-chatbot";
  
  // Optional: Custom auth token for secure access
  window.__initial_auth_token = "YOUR_CUSTOM_TOKEN";
</script>
```

**Get Firebase Config:**

1. Go to Firebase Console → Project Settings
2. Scroll to "Your apps"
3. Click on your web app or create one
4. Copy the `firebaseConfig` object

---

## 🚀 Usage

### Backend: Start Saving Leads

```bash
cd backend
python main.py
```

Now when users:
- Request a demo → Saved to Firestore
- Ask for human help → Saved to Firestore
- Upload RFP → Saved to Firestore
- Apply for jobs → Saved to Firestore

### Frontend: View Dashboard

```bash
cd frontend
npm run dev
```

Navigate to: `http://localhost:3000/admin/leads`

---

## 📊 Dashboard Features

### ✅ Real-Time Updates
- Uses Firebase `onSnapshot` for live updates
- No page refresh needed
- Instant notifications when new leads arrive

### ✅ Filtering
- **ALL** - View all leads
- **NEW** - Uncontacted leads
- **CONTACTED** - Leads that have been reached
- **IN_PROGRESS** - Active conversations
- **CLOSED** - Completed/resolved leads

### ✅ Status Management
- **NEW** → Click "✓ Mark as Contacted"
- **CONTACTED** → Click "⟳ In Progress"
- **IN_PROGRESS** → Click "✖ Close"
- **CLOSED** → Click "↺ Reopen"

### ✅ Admin Notes
- Add internal notes for each lead
- Track conversation history
- Share context between team members

### ✅ Lead Types

| Type | Icon | Color | Description |
|------|------|-------|-------------|
| DEMO_REQUEST | 🎯 | Blue | User requested a demo |
| HUMAN_HANDOFF | 🆘 | Red | User needs human assistance |
| RFP_UPLOAD | 📤 | Purple | RFP submission |
| CAREER_APPLICATION | 💼 | Green | Job application |

---

## 🔐 Security Configuration

### Firestore Security Rules

Update your Firestore rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write leads
    match /artifacts/{appId}/public/data/chatbot_leads/{leadId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### Authentication Options

**Option 1: Anonymous Auth (Testing)**
```javascript
// Automatically handled in the component
signInAnonymously(auth);
```

**Option 2: Custom Token (Production)**
```javascript
// Generate custom token on your backend
window.__initial_auth_token = "YOUR_SECURE_TOKEN";
```

**Option 3: Email/Password (Team Access)**
```javascript
// Add login page before dashboard
signInWithEmailAndPassword(auth, email, password);
```

---

## 🧪 Testing

### Test Backend Integration

```bash
cd backend
python -c "
from firebase_service import firebase_service

# Test lead data
test_lead = {
    'type': 'DEMO_REQUEST',
    'name': 'Test User',
    'contact': 'test@example.com',
    'info': 'Test demo request',
    'ticket_id': 'TEST123'
}

doc_id = firebase_service.save_lead_to_firestore(test_lead)
print(f'✅ Test lead saved: {doc_id}')
"
```

### Test Frontend Dashboard

1. Start the backend and trigger a demo request via chatbot
2. Open admin dashboard
3. Verify the lead appears in real-time
4. Test status updates
5. Test note saving

---

## 📱 Responsive Design

The dashboard is fully responsive:

- **Desktop**: 2-column grid layout
- **Tablet**: 1-column with optimized spacing
- **Mobile**: Single column with touch-friendly buttons

---

## 🎨 Customization

### Change Colors

Edit the Tailwind classes in `ChatResponsesDashboard.jsx`:

```jsx
// Change primary color from blue to your brand color
className="bg-blue-600" → className="bg-purple-600"
className="text-blue-600" → className="text-purple-600"
```

### Add New Lead Types

1. **Backend** (`firebase_service.py`):
```python
def format_custom_lead(self, data: Dict, ticket_id: str) -> Dict:
    return {
        'type': 'CUSTOM_TYPE',
        'name': data.get('name'),
        'contact': data.get('contact'),
        'info': data.get('info'),
        'ticket_id': ticket_id
    }
```

2. **Frontend** (`ChatResponsesDashboard.jsx`):
```jsx
// Add to getTypeColor function
'CUSTOM_TYPE': 'bg-orange-100 text-orange-800 border-orange-300'

// Add icon
{lead.type === 'CUSTOM_TYPE' && '🔔'}
```

### Add More Filters

```jsx
// Add custom filters
const [customFilter, setCustomFilter] = useState(null);

// Filter by lead type
<button onClick={() => setFilter('DEMO_REQUEST')}>
  Demos Only
</button>
```

---

## 🐛 Troubleshooting

### Issue: "Firebase not initialized"

**Solution:**
- Check `firebase-credentials.json` exists in backend folder
- Verify `FIREBASE_CREDENTIALS_PATH` in `.env`
- Ensure Firebase Admin SDK is installed: `pip install firebase-admin`

### Issue: "Permission denied" on Firestore

**Solution:**
- Update Firestore security rules (see Security Configuration)
- Verify authentication is working
- Check Firebase Console → Authentication is enabled

### Issue: "No leads appearing"

**Solution:**
- Check browser console for errors
- Verify `window.__firebase_config` is set correctly
- Test backend is saving leads (check Firestore console)
- Ensure collection path matches: `/artifacts/{appId}/public/data/chatbot_leads`

### Issue: "Auth state not changing"

**Solution:**
- Enable Anonymous Authentication in Firebase Console
- Or provide valid `__initial_auth_token`
- Check Network tab for auth errors

---

## 📈 Analytics & Monitoring

### Track Lead Metrics

Add to your dashboard:

```jsx
// Calculate stats
const newLeads = leads.filter(l => l.status === 'NEW').length;
const conversionRate = (contactedLeads / totalLeads * 100).toFixed(1);
const avgResponseTime = calculateAvgTime(leads);
```

### Export Leads

```jsx
const exportToCSV = () => {
  const csv = leads.map(lead => 
    `${lead.name},${lead.contact},${lead.type},${lead.status}`
  ).join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'leads.csv';
  a.click();
};
```

---

## ✅ Checklist

### Backend Setup
- [ ] Install `firebase-admin`
- [ ] Download Firebase credentials JSON
- [ ] Add `FIREBASE_APP_ID` to `.env`
- [ ] Test lead saving with demo request
- [ ] Verify data in Firebase Console

### Frontend Setup
- [ ] Install `firebase` npm package
- [ ] Set `window.__firebase_config`
- [ ] Add dashboard route
- [ ] Test real-time updates
- [ ] Configure Firestore security rules

### Production Checklist
- [ ] Secure authentication (custom tokens or email/password)
- [ ] Update Firestore rules for production
- [ ] Add monitoring and logging
- [ ] Set up backup strategy
- [ ] Document admin access procedures

---

## 🎉 You're Done!

Your chatbot now:
✅ Saves all leads to Firebase Firestore automatically
✅ Provides real-time admin dashboard for lead management
✅ Tracks lead status and internal notes
✅ Handles multiple lead types (demo, handoff, RFP, careers)

**Next Steps:**
1. Customize the dashboard design
2. Add email notifications for new leads
3. Integrate with CRM systems
4. Add analytics and reporting

---

**Need Help?** Check the Firebase Console for real-time data and errors, or review the browser console for debugging information.
