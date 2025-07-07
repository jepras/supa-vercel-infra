#!/usr/bin/env python3
"""
Simple test script to verify OpenRouter connectivity.
Run this after setting up your OpenRouter API key.
"""

import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter():
    """Test OpenRouter connectivity with a simple message."""
    
    # Check if API key is configured
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("Please set your OpenRouter API key in .env file or environment")
        return False
    
    print(f"✅ OpenRouter API key found: {api_key[:10]}...")
    
    # Configure OpenRouter client
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Test with a simple message
    test_message = "Hello! Please respond with 'OpenRouter is working!' if you can see this message."
    
    try:
        print("🔄 Testing OpenRouter connection...")
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # Use a cheaper model for testing
            messages=[{"role": "user", "content": test_message}],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenRouter test successful!")
        print(f"Response: {result}")
        print(f"Model used: {response.model}")
        print(f"Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter test failed: {str(e)}")
        return False

def test_models():
    """Test different models to see which ones are available."""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    models_to_test = [
        "openai/gpt-4-1106-preview",
        "openai/gpt-3.5-turbo", 
        "anthropic/claude-3-sonnet",
        "google/gemini-pro",
        "meta-llama/llama-2-70b-chat"
    ]
    
    print("\n🔄 Testing model availability...")
    
    for model in models_to_test:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10,
                temperature=0.1
            )
            print(f"✅ {model} - Available")
        except Exception as e:
            print(f"❌ {model} - Not available: {str(e)}")

if __name__ == "__main__":
    print("🚀 OpenRouter Connectivity Test")
    print("=" * 40)
    
    # Test basic connectivity
    success = test_openrouter()
    
    if success:
        # Test model availability
        test_models()
        
        print("\n" + "=" * 40)
        print("✅ OpenRouter setup is complete!")
        print("You can now run the Jupyter notebooks for AI analysis.")
        print("\nNext steps:")
        print("1. Run: jupyter notebook notebooks/ai_analysis_prototype.ipynb")
        print("2. Run: jupyter notebook notebooks/model_comparison.ipynb")
        print("3. Run: jupyter notebook notebooks/cost_optimization.ipynb")
    else:
        print("\n❌ Please fix the OpenRouter configuration and try again.") 