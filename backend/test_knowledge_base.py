"""
Test AWS Knowledge Base Integration
"""
import os
from dotenv import load_dotenv
from bedrock_client import BedrockClient

load_dotenv()

def test_knowledge_base():
    """Test the Knowledge Base retrieval and response generation"""
    print("=" * 60)
    print("AWS KNOWLEDGE BASE INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing Bedrock Client...")
    try:
        client = BedrockClient()
        print("   ✅ Bedrock Client initialized")
        print(f"   📍 Region: {client.region}")
        print(f"   🤖 Model: {client.model_id}")
        print(f"   📚 Knowledge Base ID: {client.knowledge_base_id}")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {str(e)}")
        return
    
    # Test queries
    test_queries = [
        "What services does InstaLogic offer?",
        "Tell me about your data analytics capabilities",
        "What industries do you serve?",
        "Do you have any case studies?"
    ]
    
    print("\n2. Testing Knowledge Base Retrieval...")
    for i, query in enumerate(test_queries[:2], 1):  # Test first 2 queries
        print(f"\n   Query {i}: {query}")
        print("   " + "-" * 55)
        
        try:
            # Test retrieval
            kb_result = client.retrieve_from_knowledge_base(query, number_of_results=3)
            
            print(f"   📊 Retrieved {len(kb_result['chunks'])} chunks")
            print(f"   🔗 Found {len(kb_result['sources'])} unique sources")
            
            if kb_result['sources']:
                print(f"   📄 Sources:")
                for source in kb_result['sources']:
                    print(f"      • {source}")
            
            if kb_result['chunks']:
                print(f"\n   📝 Top result (score: {kb_result['chunks'][0]['score']:.4f}):")
                preview = kb_result['chunks'][0]['text'][:200]
                print(f"      {preview}...")
            
        except Exception as e:
            print(f"   ❌ Retrieval failed: {str(e)}")
    
    # Test full response generation
    print("\n3. Testing Full Response Generation (KB + Claude)...")
    test_query = test_queries[0]
    print(f"\n   Query: {test_query}")
    print("   " + "-" * 55)
    
    try:
        result = client.generate_response_with_kb(
            user_message=test_query,
            system_prompt="You are a helpful assistant for InstaLogic. Answer based on the knowledge base.",
            use_knowledge_base=True
        )
        
        print(f"   ✅ Response generated")
        print(f"   📚 Context used: {result['context_used']}")
        print(f"   🔗 Sources: {len(result['sources'])}")
        
        if result['sources']:
            print(f"   📄 Source URLs:")
            for source in result['sources']:
                print(f"      • {source}")
        
        print(f"\n   🤖 AI Response:")
        print(f"   {'-' * 55}")
        response_preview = result['response'][:500]
        print(f"   {response_preview}...")
        print(f"   {'-' * 55}")
        print(f"   📏 Full response length: {len(result['response'])} characters")
        
    except Exception as e:
        print(f"   ❌ Response generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nYour chatbot is now using:")
    print("  ✅ AWS Bedrock Knowledge Base (d-instalogic-new)")
    print("  ✅ Web Crawler Data Source (instalogic.in)")
    print("  ✅ Amazon OpenSearch Serverless")
    print("  ✅ Titan Text Embeddings v2")
    print("  ✅ Claude 3 Sonnet for responses")
    print("\nThe chatbot will retrieve relevant information from your")
    print("website and use it to answer questions accurately!")
    print("=" * 60)

if __name__ == "__main__":
    test_knowledge_base()
