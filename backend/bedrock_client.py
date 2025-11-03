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
    
    def _map_s3_to_website(self, content: str) -> str:
        """
        Map S3 content to relevant InstaLogic website pages based on keywords
        """
        content_lower = content.lower()
        
        # Check for specific topics and map to relevant pages
        if any(keyword in content_lower for keyword in ['case study', 'case studies', 'project', 'client work', 'success story']):
            return 'https://www.instalogic.in/case-studies/'
        elif any(keyword in content_lower for keyword in ['service', 'offering', 'solution', 'capability', 'what we do']):
            return 'https://www.instalogic.in/our-services/'
        elif any(keyword in content_lower for keyword in ['career', 'job', 'hiring', 'position', 'opening', 'work with us', 'join our team']):
            return 'https://www.instalogic.in/careers/'
        elif any(keyword in content_lower for keyword in ['about us', 'our story', 'history', 'mission', 'vision', 'values']):
            return 'https://www.instalogic.in/our-story/'
        elif any(keyword in content_lower for keyword in ['contact', 'reach us', 'get in touch', 'email', 'phone', 'address']):
            return 'https://www.instalogic.in/contact-us/'
        else:
            # Default to homepage
            return 'https://www.instalogic.in/'
    
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
                metadata = result.get('metadata', {})
                
                # Extract source URI from various possible locations
                location = result.get('location', {})
                source_uri = ''
                
                # Priority 1: Check metadata for x-amz-bedrock-kb-source-uri (original web URL)
                if 'x-amz-bedrock-kb-source-uri' in metadata:
                    source_uri = metadata['x-amz-bedrock-kb-source-uri']
                # Priority 2: Check for webLocation
                elif 'webLocation' in location:
                    source_uri = location['webLocation'].get('url', '')
                # Priority 3: S3 location - check actual structure
                elif 's3Location' in location:
                    s3_uri = location['s3Location'].get('uri', '')
                    # Convert S3 URI to website URL based on content
                    if s3_uri:
                        source_uri = self._map_s3_to_website(content)
                # Priority 4: Check location type field
                elif 'type' in location:
                    if location['type'] == 'S3':
                        source_uri = self._map_s3_to_website(content)
                
                # Final fallback: If still no source_uri, map based on content
                if not source_uri:
                    source_uri = self._map_s3_to_website(content)
                
                
                if content:
                    retrieved_chunks.append({
                        'text': content,
                        'score': score,
                        'source': source_uri
                    })
                    if source_uri and source_uri not in sources:
                        sources.append(source_uri)
            
            # Clean up sources: convert any remaining S3 URIs to website URLs
            cleaned_sources = []
            for source in sources:
                if source.startswith('s3://'):
                    # Find the corresponding chunk content to map to website
                    matching_chunk = next((chunk for chunk in retrieved_chunks if chunk['source'] == source), None)
                    if matching_chunk:
                        website_url = self._map_s3_to_website(matching_chunk['text'])
                        if website_url not in cleaned_sources:
                            cleaned_sources.append(website_url)
                else:
                    if source not in cleaned_sources:
                        cleaned_sources.append(source)
            
            return {
                'chunks': retrieved_chunks,
                'sources': cleaned_sources,
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
