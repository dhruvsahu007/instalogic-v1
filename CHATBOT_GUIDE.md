# 🤖 InstaLogic AI Chatbot - Complete Setup

## 🎯 What We Built

A **fully functional AI-powered chatbot** for the InstaLogic website using:
- ✅ **AWS Bedrock** (Claude 3 AI models)
- ✅ **FastAPI** backend with conversation management
- ✅ **React** frontend with beautiful UI
- ✅ **Intent detection** and quick replies
- ✅ **Multi-turn conversations** with history
- ✅ **Demo requests** and contact forms

---

## 📁 Project Structure

```
InstaLogic/
├── backend/
│   ├── main.py                 # FastAPI app with chatbot endpoints
│   ├── bedrock_client.py       # AWS Bedrock integration
│   ├── knowledge_base.py       # Company knowledge from qna.txt
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── test_setup.py          # Setup test script
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chatbot.jsx    # AI chat component
│   │   │   ├── Chatbot.css    # Chat styling
│   │   │   └── ... (other components)
│   │   ├── App.jsx            # Main app (includes chatbot)
│   │   └── ...
│   └── package.json
│
├── AWS_BEDROCK_SETUP.md       # Complete AWS setup guide
├── qna.txt                    # Your Q&A document
└── README.md
```

---

## 🚀 Quick Start

### Step 1: AWS Setup (CRITICAL!)

You need to set up AWS Bedrock access first. Follow the detailed guide in `AWS_BEDROCK_SETUP.md`:

1. Enable AWS Bedrock model access (Claude 3)
2. Create IAM user with Bedrock permissions
3. Get AWS access keys
4. Configure `.env` file

**⚠️ The chatbot WILL NOT WORK without proper AWS setup!**

### Step 2: Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment file
copy .env.example .env
# Edit .env with your AWS credentials

# Test the setup
python test_setup.py

# Start the backend
python main.py
```

Backend runs on: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Step 3: Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

---

## 🎨 Features

### 1. AI-Powered Conversations
- Uses AWS Bedrock Claude 3 models
- Understands company knowledge from qna.txt
- Maintains conversation context
- Natural language understanding

### 2. Intent Detection
The bot automatically detects what users want:
- **Services** - Shows service information
- **Demo Request** - Guides through demo booking
- **Case Studies** - Shares past work examples
- **Pricing** - Provides pricing information
- **Contact** - Collects contact information
- **Careers** - Directs to job opportunities

### 3. Quick Reply Buttons
Contextual buttons that appear based on conversation:
- "View Our Services"
- "Request a Demo"
- "See Case Studies"
- "Contact Sales"
- "Career Opportunities"

### 4. Multi-Turn Conversations
- Remembers conversation history
- Provides contextual responses
- Follows up on previous topics
- Session management

### 5. Transactional Flows
- **Demo Requests**: Collects name, email, industry, preferences
- **RFP Upload**: Handles project briefs and requirements
- **Contact Forms**: Connects users with the right team

---

## 📋 API Endpoints

### Chat Endpoints

```bash
# Send a message (main chatbot endpoint)
POST /api/chat
{
  "message": "What services do you offer?",
  "session_id": "optional-uuid"
}

# Get conversation history
GET /api/chat/history/{session_id}

# Delete a session
DELETE /api/chat/session/{session_id}

# Get all active sessions (admin)
GET /api/chat/sessions
```

### Demo & Contact Endpoints

```bash
# Request a demo
POST /api/demo-request
{
  "name": "John Doe",
  "email": "john@example.com",
  "industry": "Finance",
  "message": "Interested in dashboards"
}

# Upload RFP
POST /api/rfp-upload
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "company": "ABC Corp",
  "project_brief": "Need analytics solution"
}

# Get all demo requests (admin)
GET /api/demo-requests
```

---

## 🧪 Testing the Chatbot

### Test Questions to Try:

**About Company:**
- "Who is InstaLogic?"
- "What does InstaLogic do?"
- "Tell me about your company"

**Services:**
- "What services do you offer?"
- "Tell me about Data Analytics"
- "Do you provide training?"
- "What are your e-governance solutions?"

**Case Studies:**
- "Show me your case studies"
- "What projects have you done?"
- "Tell me about MBOCWWB dashboard"

**Pricing & Quotes:**
- "How much does a dashboard cost?"
- "Can I get a quote?"
- "What's your pricing model?"

**Demo Requests:**
- "I want a demo"
- "Can you show me a demonstration?"
- "I'd like to see a proof of concept"

**Technical:**
- "What BI tools do you use?"
- "Do you work with Power BI?"
- "Can you integrate with our database?"

**Contact:**
- "How can I contact you?"
- "I want to speak to sales"
- "Can I schedule a call?"

**Careers:**
- "Are you hiring?"
- "What jobs are available?"
- "How can I apply?"

---

## 🎨 Chatbot UI Features

1. **Floating Chat Button**
   - Blue gradient button in bottom-right
   - "AI" badge indicator
   - Smooth animations

2. **Chat Window**
   - Clean, modern design
   - Responsive (works on mobile)
   - Smooth scrolling
   - Typing indicators

3. **Message Bubbles**
   - User messages: Blue gradient, right-aligned
   - Bot messages: White, left-aligned
   - Timestamps for each message

4. **Quick Reply Buttons**
   - Contextual suggestions
   - One-click responses
   - Changes based on conversation

5. **Input Area**
   - Auto-expanding textarea
   - Send button with icon
   - Enter to send, Shift+Enter for new line

6. **Header Actions**
   - Clear chat button
   - Close button
   - Online status indicator

---

## 💰 Cost Estimation

### AWS Bedrock Pricing

**Claude 3 Haiku** (Recommended for development):
- Input: $0.25 per 1M tokens (~$0.0002 per message)
- Output: $1.25 per 1M tokens (~$0.001 per message)

**Estimated costs:**
- 100 conversations/day = ~$3-5/month
- 1,000 conversations/day = ~$30-50/month

Very affordable for a production chatbot!

---

## 🔒 Security Notes

1. ✅ `.env` file is in `.gitignore` (never commit secrets)
2. ✅ CORS configured for specific origins
3. ✅ Session management with unique IDs
4. ⚠️ Add rate limiting for production
5. ⚠️ Add authentication for admin endpoints
6. ⚠️ Use AWS Secrets Manager in production

---

## 🚨 Important: Knowledge Base Option

### Current Implementation:
Knowledge is embedded in `backend/knowledge_base.py` (from your qna.txt)

### Alternative: AWS Bedrock Knowledge Base

If you want more advanced RAG (Retrieval-Augmented Generation):

1. Create a Bedrock Knowledge Base in AWS Console
2. Upload your qna.txt as a data source
3. Use the Retrieve API to fetch relevant context
4. More expensive but more scalable

**For now, the embedded approach works great and is much simpler!**

---

## 🐛 Troubleshooting

### "AccessDeniedException"
→ Check AWS credentials in `.env`
→ Verify Bedrock model access is enabled
→ Check IAM permissions

### Chat button doesn't appear
→ Check browser console for errors
→ Verify backend is running
→ Check CORS settings

### Slow responses
→ Switch to Claude 3 Haiku (faster)
→ Reduce conversation history length

### No response from bot
→ Check backend logs
→ Verify AWS credentials are correct
→ Test with `python test_setup.py`

---

## 📚 Files You Need to Know

### Backend Files:
- `main.py` - API endpoints and routing
- `bedrock_client.py` - AWS Bedrock integration
- `knowledge_base.py` - Company knowledge and intents
- `.env` - Your AWS credentials (CREATE THIS!)

### Frontend Files:
- `components/Chatbot.jsx` - Chat UI component
- `components/Chatbot.css` - Chat styling
- `App.jsx` - Includes chatbot in main app

### Documentation:
- `AWS_BEDROCK_SETUP.md` - Detailed AWS setup guide
- `README.md` - Project overview
- `qna.txt` - Your original Q&A document

---

## ✅ Next Steps

1. **Setup AWS Bedrock** (see `AWS_BEDROCK_SETUP.md`)
2. **Configure `.env`** with your AWS credentials
3. **Run test script**: `python backend/test_setup.py`
4. **Start backend**: `python backend/main.py`
5. **Start frontend**: `npm run dev` in frontend folder
6. **Test the chatbot** on http://localhost:3000

---

## 🎉 You're All Set!

Your AI chatbot is ready to:
- Answer questions about InstaLogic
- Help users book demos
- Provide service information
- Share case studies
- Connect users with sales
- Guide career applications

The chatbot uses the knowledge from your `qna.txt` file and can handle all 18 question categories!

---

## 🆘 Need Help?

1. Read `AWS_BEDROCK_SETUP.md` for AWS configuration
2. Run `python backend/test_setup.py` to diagnose issues
3. Check API docs at `http://localhost:8000/docs`
4. Check browser console for frontend errors
5. Check terminal for backend errors

---

**Happy Chatting! 🤖💬**
