"""
AWS Bedrock Client for AI-powered chatbot
"""
import boto3
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class BedrockClient:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID", 
            "anthropic.claude-3-sonnet-20240229-v1:0"
        )
        self.knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "RJGVI4DQRM")
        
        # Initialize Bedrock Runtime client
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        
        # Initialize Bedrock Agent Runtime client for Knowledge Base
        self.agent_client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    
    def invoke_claude(
        self, 
        prompt: str, 
        system_prompt: str = "",
        conversation_history: List[Dict] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke Claude model via Bedrock
        """
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        # Invoke the model
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        
        # Extract the text from Claude's response
        if "content" in response_body and len(response_body["content"]) > 0:
            return response_body["content"][0]["text"]
        
        return "I apologize, but I couldn't generate a response. Please try again."
    
    def invoke_titan(
        self, 
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke Amazon Titan model via Bedrock
        """
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 0.9
            }
        }
        
        response = self.client.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps(body)
        )
        
        response_body = json.loads(response["body"].read())
        
        if "results" in response_body and len(response_body["results"]) > 0:
            return response_body["results"][0]["outputText"]
        
        return "I apologize, but I couldn't generate a response. Please try again."
    
    def retrieve_from_knowledge_base(
        self,
        query: str,
        number_of_results: int = 5
    ) -> Dict:
        """
        Query AWS Knowledge Base for relevant information
        Returns retrieved context and sources
        """
        try:
            response = self.agent_client.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': number_of_results
                    }
                }
            )
            
            # Extract retrieved chunks
            retrieved_chunks = []
            sources = []
            
            for result in response.get('retrievalResults', []):
                content = result.get('content', {}).get('text', '')
                score = result.get('score', 0)
                source_uri = result.get('location', {}).get('webLocation', {}).get('url', '')
                
                if content:
                    retrieved_chunks.append({
                        'text': content,
                        'score': score,
                        'source': source_uri
                    })
                    if source_uri and source_uri not in sources:
                        sources.append(source_uri)
            
            return {
                'chunks': retrieved_chunks,
                'sources': sources,
                'context': '\n\n'.join([chunk['text'] for chunk in retrieved_chunks])
            }
        
        except Exception as e:
            print(f"Error retrieving from knowledge base: {str(e)}")
            return {
                'chunks': [],
                'sources': [],
                'context': ''
            }
    
    def generate_response_with_kb(
        self,
        user_message: str,
        system_prompt: str = "",
        conversation_history: List[Dict] = None,
        use_knowledge_base: bool = True
    ) -> Dict:
        """
        Generate response using AWS Knowledge Base + Claude
        Returns both the response and sources
        """
        context = ""
        sources = []
        
        # Retrieve from Knowledge Base if enabled
        if use_knowledge_base:
            kb_results = self.retrieve_from_knowledge_base(user_message)
            context = kb_results['context']
            sources = kb_results['sources']
        
        # Enhance system prompt with retrieved context
        enhanced_prompt = system_prompt
        if context:
            enhanced_prompt = f"""{system_prompt}

RETRIEVED CONTEXT FROM KNOWLEDGE BASE:
{context}

Use the above context to answer the user's question. If the context doesn't contain relevant information, use your general knowledge about InstaLogic."""
        
        # Generate response with Claude
        response = self.invoke_claude(
            prompt=user_message,
            system_prompt=enhanced_prompt,
            conversation_history=conversation_history
        )
        
        return {
            'response': response,
            'sources': sources,
            'context_used': bool(context)
        }
    
    def generate_response(
        self,
        user_message: str,
        system_prompt: str = "",
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Main method to generate chatbot responses
        """
        # Use Claude by default (supports conversation history better)
        if "claude" in self.model_id.lower():
            return self.invoke_claude(
                prompt=user_message,
                system_prompt=system_prompt,
                conversation_history=conversation_history
            )
        elif "titan" in self.model_id.lower():
            # Titan doesn't support conversation history the same way
            full_prompt = system_prompt + "\n\n" + user_message
            return self.invoke_titan(prompt=full_prompt)
        else:
            raise ValueError(f"Unsupported model: {self.model_id}")
