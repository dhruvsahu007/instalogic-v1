# AWS Knowledge Base Integration

## Overview

Your InstaLogic chatbot now uses **AWS Bedrock Knowledge Base** to retrieve accurate, up-to-date information directly from your website (https://www.instalogic.in/).

## Architecture

```
User Question
     ↓
Knowledge Base Retrieval (Vector Search)
     ↓
Top 5 Relevant Chunks from Website
     ↓
Claude 3 Sonnet (Response Generation)
     ↓
AI Response + Source URLs
```

## Components

### 1. **AWS Knowledge Base**
- **ID**: `RJGVI4DQRM`
- **Name**: `d-instalogic-new`
- **Type**: Retrieval-Augmented Generation (RAG)
- **Status**: ✅ Available

### 2. **Data Source**
- **Type**: Web Crawler
- **Source**: https://www.instalogic.in/
- **Status**: ✅ Available
- **Chunking**: Default strategy
- **Parsing**: Default strategy

### 3. **Vector Store**
- **Type**: Amazon OpenSearch Serverless
- **Collection ARN**: `arn:aws:aoss:us-east-1:926944000247:collection/hmdyj4f2eadiwxhniqm7`
- **Index Name**: `bedrock-knowledge-base-default-index`

### 4. **Embeddings Model**
- **Model**: Titan Text Embeddings v2
- **Type**: Float vector embeddings
- **Dimensions**: 1024

### 5. **Response Generation**
- **Model**: Claude 3 Sonnet
- **Model ID**: `anthropic.claude-3-sonnet-20240229-v1:0`

## How It Works

### Query Flow

1. **User asks a question** → "What services does InstaLogic offer?"

2. **Vector Search** → Knowledge Base searches your website content using semantic similarity

3. **Retrieve Top Results** → Gets 5 most relevant chunks with confidence scores

4. **Context Injection** → Sends retrieved content + user question to Claude

5. **AI Response** → Claude generates answer using the retrieved context

6. **Source Attribution** → Response includes URLs where information was found

### Example Response

**User**: "What are your data analytics capabilities?"

**AI Response**: "InstaLogic offers comprehensive data analytics and business intelligence solutions including..."

**Sources**:
- https://www.instalogic.in/services
- https://www.instalogic.in/solutions/analytics

## Configuration

### Environment Variables (.env)

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# AWS Knowledge Base Configuration
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
```

### Code Integration

**Backend (main.py)**:
```python
# Generate response using AWS Knowledge Base + Bedrock
result = bedrock_client.generate_response_with_kb(
    user_message=user_message,
    system_prompt=SYSTEM_PROMPT,
    conversation_history=conversation_history,
    use_knowledge_base=True  # Set to False to disable KB
)

ai_response = result['response']
sources = result.get('sources', [])
```

**BedrockClient (bedrock_client.py)**:
```python
# Retrieve from Knowledge Base
kb_results = self.retrieve_from_knowledge_base(
    query=user_message,
    number_of_results=5
)

# Generate response with retrieved context
response = self.invoke_claude(
    prompt=user_message,
    system_prompt=enhanced_prompt,
    conversation_history=conversation_history
)
```

## Testing

### Run Knowledge Base Test

```bash
cd backend
python test_knowledge_base.py
```

This will:
1. ✅ Verify Knowledge Base connection
2. ✅ Test retrieval with sample queries
3. ✅ Show retrieved chunks and scores
4. ✅ Display source URLs
5. ✅ Generate full AI response

### Expected Output

```
==================================================
AWS KNOWLEDGE BASE INTEGRATION TEST
==================================================

1. Initializing Bedrock Client...
   ✅ Bedrock Client initialized
   📍 Region: us-east-1
   🤖 Model: anthropic.claude-3-sonnet-20240229-v1:0
   📚 Knowledge Base ID: RJGVI4DQRM

2. Testing Knowledge Base Retrieval...
   Query 1: What services does InstaLogic offer?
   -------------------------------------------------------
   📊 Retrieved 3 chunks
   🔗 Found 2 unique sources
   📄 Sources:
      • https://www.instalogic.in/services
      • https://www.instalogic.in/

3. Testing Full Response Generation (KB + Claude)...
   ✅ Response generated
   📚 Context used: True
   🔗 Sources: 2
```

## Benefits

### ✅ **Accuracy**
- Answers based on actual website content
- No hallucination or outdated information
- Source attribution for transparency

### ✅ **Scalability**
- Automatically updates when website changes
- No manual knowledge base editing required
- Handles large content volumes

### ✅ **Performance**
- Fast vector search (< 1 second)
- Relevant results with confidence scores
- Efficient chunk retrieval

### ✅ **Maintenance**
- Web crawler keeps data fresh
- No code changes needed for content updates
- Automatic re-indexing

## Syncing Data

### Trigger Manual Sync

To update the Knowledge Base with latest website content:

1. Go to **AWS Console** → **Bedrock** → **Knowledge Bases**
2. Select `d-instalogic-new`
3. Go to **Data Sources** tab
4. Click **Sync** on `instalogic-website`
5. Wait for sync to complete (few minutes to hours)

### Auto-Sync (Optional)

You can configure automatic syncing:
- Edit data source settings
- Set sync schedule (daily/weekly)
- Knowledge Base stays fresh automatically

## Customization

### Adjust Number of Results

```python
# Retrieve more chunks for detailed answers
kb_results = client.retrieve_from_knowledge_base(
    query=user_message,
    number_of_results=10  # Default: 5
)
```

### Toggle Knowledge Base

```python
# Use embedded knowledge instead of KB
result = bedrock_client.generate_response_with_kb(
    user_message=user_message,
    system_prompt=SYSTEM_PROMPT,
    use_knowledge_base=False  # Disable KB retrieval
)
```

### Add More Data Sources

In AWS Console:
1. Go to Knowledge Base → Data Sources
2. Click **Add**
3. Choose type (S3, Web Crawler, Confluence, etc.)
4. Configure and sync

## Cost Estimate

### Knowledge Base Costs

- **OpenSearch Serverless**: ~$10-20/month (for small collections)
- **Embeddings**: $0.0001 per 1000 tokens (Titan v2)
- **Retrieval**: No additional cost
- **Claude 3 Sonnet**: $3 per 1M input tokens, $15 per 1M output tokens

### Example Monthly Cost (1000 queries)
- Embeddings: ~$0.50
- Vector Store: ~$15
- Claude Inference: ~$5
- **Total**: ~$20-25/month

## Troubleshooting

### Issue: "Knowledge Base not found"
**Solution**: Verify `KNOWLEDGE_BASE_ID` in `.env` matches AWS console

### Issue: "No results retrieved"
**Solution**: 
- Check if data source sync is complete
- Verify website is accessible
- Try different query phrasing

### Issue: "Access denied"
**Solution**:
- Verify IAM permissions include `bedrock:Retrieve`
- Check AWS credentials have Knowledge Base access

### Issue: "Timeout errors"
**Solution**:
- Increase timeout in boto3 config
- Check AWS region matches Knowledge Base region

## Monitoring

### View Metrics (AWS Console)

1. Go to **CloudWatch**
2. Search for "Bedrock" metrics
3. Monitor:
   - Retrieval latency
   - Number of queries
   - Error rates

## Next Steps

### 1. **Test the Integration**
```bash
python test_knowledge_base.py
```

### 2. **Start the Chatbot**
```bash
# Backend
python main.py

# Frontend (new terminal)
cd ../frontend
npm run dev
```

### 3. **Try Sample Questions**
- "What services does InstaLogic provide?"
- "Tell me about your case studies"
- "What industries do you work with?"
- "How can I request a demo?"

### 4. **Monitor Performance**
- Check response accuracy
- Verify source URLs are correct
- Review retrieval scores in logs

## Resources

- [AWS Bedrock Knowledge Bases Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [Titan Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [Claude 3 Models](https://docs.anthropic.com/claude/docs/models-overview)

---

**🎉 Your chatbot is now powered by AWS Knowledge Base!**

It will provide accurate, source-backed answers directly from your website content.
