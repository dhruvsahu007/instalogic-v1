"""
Test script for AWS Bedrock chatbot
Run this to verify your setup is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_variables():
    """Test if environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "AWS_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "BEDROCK_MODEL_ID"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("👉 Please set these in your .env file")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_boto3():
    """Test if boto3 is installed"""
    print("\n🔍 Checking boto3 installation...")
    try:
        import boto3
        print(f"✅ boto3 version {boto3.__version__} installed")
        return True
    except ImportError:
        print("❌ boto3 not installed")
        print("👉 Run: pip install boto3")
        return False

def test_bedrock_client():
    """Test Bedrock client initialization"""
    print("\n🔍 Testing Bedrock client...")
    try:
        from bedrock_client import BedrockClient
        client = BedrockClient()
        print(f"✅ Bedrock client initialized")
        print(f"   Region: {client.region}")
        print(f"   Model: {client.model_id}")
        return True, client
    except Exception as e:
        print(f"❌ Failed to initialize Bedrock client: {e}")
        return False, None

def test_bedrock_connection():
    """Test actual connection to Bedrock"""
    print("\n🔍 Testing Bedrock API connection...")
    try:
        import boto3
        client = boto3.client(
            service_name="bedrock",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # List foundation models
        response = client.list_foundation_models()
        print(f"✅ Connected to AWS Bedrock")
        print(f"   Available models: {len(response['modelSummaries'])}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Bedrock: {e}")
        print("👉 Check your AWS credentials and permissions")
        return False

def test_model_inference():
    """Test actual model inference"""
    print("\n🔍 Testing model inference...")
    try:
        from bedrock_client import BedrockClient
        client = BedrockClient()
        
        test_message = "Hello! Can you tell me what InstaLogic does?"
        print(f"   Sending test message: '{test_message}'")
        
        response = client.generate_response(
            user_message=test_message,
            system_prompt="You are a helpful assistant for InstaLogic."
        )
        
        print(f"✅ Model inference successful!")
        print(f"   Response length: {len(response)} characters")
        print(f"   Response preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Model inference failed: {e}")
        print("👉 Check your model access in AWS Bedrock console")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 InstaLogic Chatbot - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_env_variables),
        ("Boto3 Installation", test_boto3),
        ("Bedrock Client", lambda: test_bedrock_client()[0]),
        ("Bedrock Connection", test_bedrock_connection),
        ("Model Inference", test_model_inference)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your chatbot is ready to use!")
        print("\n👉 Next steps:")
        print("   1. Start backend: python main.py")
        print("   2. Start frontend: cd ../frontend && npm run dev")
        print("   3. Open http://localhost:3000 and test the chat!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("👉 Refer to AWS_BEDROCK_SETUP.md for detailed setup instructions")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
