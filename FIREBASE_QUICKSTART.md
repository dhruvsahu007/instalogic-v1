# Firebase Integration - Quick Start

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
pip install firebase-admin
```

**Frontend:**
```bash
cd frontend
npm install firebase
```

### Step 2: Get Firebase Credentials

1. Go to https://console.firebase.google.com/
2. Select your project (or create new)
3. Go to Settings ⚙️ → Project Settings → Service Accounts
4. Click **"Generate New Private Key"**
5. Save as `backend/firebase-credentials.json`

### Step 3: Configure Backend

Add to `backend/.env`:
```bash
FIREBASE_APP_ID=instalogic-chatbot
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### Step 4: Configure Frontend

Get your Firebase config:
1. Firebase Console → Project Settings → General
2. Scroll to "Your apps"
3. Copy the `firebaseConfig`

Add to your HTML (before loading React):
```html
<script>
  window.__firebase_config = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abc"
  };
  window.__app_id = "instalogic-chatbot";
</script>
```

### Step 5: Enable Firebase Authentication

1. Firebase Console → Authentication
2. Click **"Get Started"**
3. Enable **"Anonymous"** sign-in method
4. Click **"Save"**

### Step 6: Set Firestore Rules

Firebase Console → Firestore Database → Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /artifacts/{appId}/public/data/chatbot_leads/{leadId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

Click **"Publish"**

### Step 7: Test!

**Start Backend:**
```bash
cd backend
python main.py
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Test the Flow:**
1. Open chatbot: http://localhost:3000
2. Say: "I want a demo"
3. Complete the demo request flow
4. Open admin dashboard: http://localhost:3000/admin/leads
5. See your lead appear in real-time! 🎉

---

## 📂 Files Created

### Backend
✅ `backend/firebase_service.py` - Firebase integration
✅ `backend/chatbot_orchestrator.py` - Updated with lead saving
✅ `backend/requirements.txt` - Added firebase-admin

### Frontend
✅ `frontend/src/components/ChatResponsesDashboard.jsx` - Admin dashboard

---

## 🎯 What Gets Saved?

Every time a user completes a flow:

| Flow Type | Saved As | Contains |
|-----------|----------|----------|
| Demo Request | `DEMO_REQUEST` | Name, email, industry, preferred date |
| Human Handoff | `HUMAN_HANDOFF` | Original query, urgency marker |
| RFP Upload | `RFP_UPLOAD` | Company, email, project brief |
| Career Application | `CAREER_APPLICATION` | Name, email, desired position |

---

## 📊 Dashboard Features

✅ **Real-time updates** - No refresh needed
✅ **Filter by status** - NEW, CONTACTED, IN_PROGRESS, CLOSED
✅ **Status workflow** - One-click status updates
✅ **Admin notes** - Add internal notes to each lead
✅ **Responsive design** - Works on desktop, tablet, mobile
✅ **Professional UI** - Modern Tailwind CSS design

---

## 🐛 Common Issues

### "Firebase not initialized"
→ Make sure `firebase-credentials.json` exists in `backend/` folder

### "Permission denied"
→ Check Firestore rules allow authenticated users

### "No leads showing"
→ Verify `window.__firebase_config` is set correctly

### "Auth not working"
→ Enable Anonymous Auth in Firebase Console

---

## 📞 Support

**See Full Documentation:** `FIREBASE_SETUP_GUIDE.md`

**Check Firebase Console:** 
- Firestore: See all saved leads
- Authentication: Check active users
- Rules: Verify security settings

---

## ✅ Success Checklist

- [ ] Backend saving leads (check console: "✅ Lead saved to Firestore")
- [ ] Frontend showing leads in real-time
- [ ] Can filter leads by status
- [ ] Can update lead status
- [ ] Can add and save notes
- [ ] Dashboard loads without errors

**All checked? You're ready for production!** 🚀
