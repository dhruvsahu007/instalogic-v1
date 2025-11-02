# AWS Bedrock Chatbot Setup Guide

## Prerequisites

1. **AWS Account** with Bedrock access enabled
2. **AWS CLI** installed and configured
3. **Python 3.11+** installed
4. **Node.js 18+** installed
5. **IAM User** with Bedrock permissions

---

## Step 1: Enable AWS Bedrock Access

### 1.1 Request Model Access in AWS Console

1. Go to AWS Console → Bedrock
2. Navigate to **"Model access"** in the left sidebar
3. Click **"Modify model access"**
4. Enable access to the following models:
   - ✅ **Anthropic Claude 3 Sonnet** (recommended)
   - ✅ **Anthropic Claude 3 Haiku** (faster, cheaper)
   - ✅ **Amazon Titan Text Express** (alternative)

5. Click **"Save changes"** and wait for approval (usually instant)

### 1.2 Verify Model Access

```bash
aws bedrock list-foundation-models --region us-east-1
```

You should see the Claude models listed.

---

## Step 2: Create IAM User with Bedrock Permissions

### 2.1 Create IAM Policy

Go to IAM → Policies → Create Policy (JSON):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    }
  ]
}
```

Name it: `BedrockChatbotPolicy`

### 2.2 Create IAM User

1. Go to IAM → Users → Add User
2. User name: `instalogic-chatbot-user`
3. Attach the `BedrockChatbotPolicy` policy
4. Create access keys (Access key ID & Secret access key)
5. **Save these credentials securely!**

---

## Step 3: Configure Backend

### 3.1 Set Up Environment Variables

1. Copy the example file:
```bash
cd backend
copy .env.example .env
```

2. Edit `.env` with your AWS credentials:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Chat Configuration
MAX_CHAT_HISTORY=10
CONVERSATION_TIMEOUT_MINUTES=30
```

### 3.2 Choose Your Model

**Available Models:**

| Model | Model ID | Best For | Cost |
|-------|----------|----------|------|
| **Claude 3 Sonnet** | `anthropic.claude-3-sonnet-20240229-v1:0` | Balanced performance | $$ |
| **Claude 3 Haiku** | `anthropic.claude-3-haiku-20240307-v1:0` | Fast responses | $ |
| **Claude 3 Opus** | `anthropic.claude-3-opus-20240229-v1:0` | Most capable | $$$ |
| **Titan Text Express** | `amazon.titan-text-express-v1` | AWS native | $ |

**Recommendation:** Start with **Claude 3 Haiku** for development (fast & cheap), upgrade to Sonnet for production.

### 3.3 Install Dependencies

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3.4 Test Backend Connection

```bash
python -c "from bedrock_client import BedrockClient; client = BedrockClient(); print('✅ Bedrock connected!')"
```

---

## Step 4: Test the Chatbot

### 4.1 Start Backend

```bash
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Backend will run on: `http://localhost:8000`

### 4.2 Test API with curl

```powershell
# Test root endpoint
curl http://localhost:8000/

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{\"message\": \"What services do you offer?\"}'
```

### 4.3 Start Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: `http://localhost:3000`

### 4.4 Test the Chatbot

1. Open `http://localhost:3000` in your browser
2. Click the blue chat button in the bottom-right corner
3. Try these test questions:
   - "What services do you offer?"
   - "Tell me about your Data Analytics services"
   - "I want to request a demo"
   - "Show me your case studies"
   - "How much does a dashboard cost?"

---

## Step 5: Verify Everything Works

### ✅ Checklist:

- [ ] AWS Bedrock model access enabled
- [ ] IAM user created with proper permissions
- [ ] `.env` file configured with AWS credentials
- [ ] Backend starts without errors
- [ ] Can access API docs at `http://localhost:8000/docs`
- [ ] Frontend starts without errors
- [ ] Chat button appears on website
- [ ] Can send messages and receive AI responses
- [ ] Quick reply buttons work
- [ ] Conversation history is maintained

---

## Step 6: Alternative - Using AWS Knowledge Base (Optional)

If you want to use AWS Bedrock Knowledge Base instead of embedding knowledge in code:

### 6.1 Create Knowledge Base

1. Go to AWS Bedrock → Knowledge bases
2. Click "Create knowledge base"
3. Upload `qna.txt` as a data source
4. Choose embedding model (Titan Embeddings recommended)
5. Create vector store (OpenSearch Serverless or Amazon Aurora)
6. Wait for indexing to complete

### 6.2 Update Backend Code

You would need to modify `bedrock_client.py` to use the Retrieve API:

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def retrieve_from_kb(query, kb_id):
    response = bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={'text': query}
    )
    return response['retrievalResults']
```

**Note:** Knowledge Base setup requires additional AWS services and incurs extra costs. The embedded knowledge approach (current implementation) is simpler and cheaper for getting started.

---

## Troubleshooting

### Problem: "AccessDeniedException"

**Solution:** Verify:
1. Model access is enabled in Bedrock console
2. IAM user has correct permissions
3. AWS credentials are correct in `.env`
4. Region is set to where Bedrock is available (us-east-1 recommended)

### Problem: "ResourceNotFoundException"

**Solution:** Check that the model ID is correct and available in your region.

### Problem: "ValidationException"

**Solution:** Verify the request format matches the model's expected input structure.

### Problem: Chat button doesn't appear

**Solution:** 
1. Check browser console for errors
2. Verify frontend can reach backend (check CORS)
3. Ensure Chatbot component is imported in App.jsx

### Problem: Slow responses

**Solution:**
1. Switch to Claude 3 Haiku (faster)
2. Reduce conversation history length
3. Optimize system prompt

---

## API Endpoints

### Chat Endpoints

```bash
# Send message
POST /api/chat
Body: {
  "message": "Your question",
  "session_id": "optional-session-id"
}

# Get chat history
GET /api/chat/history/{session_id}

# Delete session
DELETE /api/chat/session/{session_id}

# Get all sessions (admin)
GET /api/chat/sessions
```

### Demo Request

```bash
POST /api/demo-request
Body: {
  "name": "John Doe",
  "email": "john@example.com",
  "industry": "Finance",
  "message": "Interested in BI dashboards"
}
```

### RFP Upload

```bash
POST /api/rfp-upload
Body: {
  "name": "Jane Smith",
  "email": "jane@company.com",
  "company": "ABC Corp",
  "project_brief": "Need analytics dashboard for HR"
}
```

---

## Cost Estimation

### AWS Bedrock Pricing (as of 2025)

**Claude 3 Haiku:**
- Input: $0.25 per 1M tokens
- Output: $1.25 per 1M tokens

**Claude 3 Sonnet:**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Example:** 1,000 conversations (avg 500 tokens each) with Haiku:
- Cost: ~$0.75 for input + ~$1.25 for output = **~$2 per 1,000 conversations**

Very cost-effective for a chatbot!

---

## Next Steps

1. **Customize Responses:** Edit `knowledge_base.py` to add more company info
2. **Add Analytics:** Track conversation metrics
3. **Improve Intent Detection:** Add more sophisticated NLP
4. **Add Forms:** Implement demo request and RFP upload forms in UI
5. **Database:** Replace in-memory storage with PostgreSQL/MongoDB
6. **Monitoring:** Add CloudWatch logging for production
7. **Rate Limiting:** Implement rate limiting to control costs

---

## Security Best Practices

1. ✅ Never commit `.env` to version control
2. ✅ Use AWS Secrets Manager for production credentials
3. ✅ Implement rate limiting on chat endpoint
4. ✅ Add authentication for admin endpoints
5. ✅ Use HTTPS in production
6. ✅ Rotate AWS access keys regularly
7. ✅ Monitor CloudWatch for unusual activity

---

## Support

If you encounter issues:
1. Check AWS Bedrock service health
2. Review CloudWatch logs
3. Test with AWS CLI to isolate issues
4. Check IAM permissions
5. Verify model availability in your region

---

**🎉 Congratulations!** Your AI chatbot with AWS Bedrock is ready!
