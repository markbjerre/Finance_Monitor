"""
Simple OpenAI API test
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print(f"API Key loaded: {api_key[:20]}...{api_key[-10:]}")
print(f"Key length: {len(api_key)}")

# Create client and test
client = OpenAI(api_key=api_key)

print("\nSending test message to OpenAI...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say 'API working!' if you can read this"}
    ],
    max_tokens=10
)

print(f"✓ Success! Response: {response.choices[0].message.content}")
print(f"Model used: {response.model}")
print(f"Tokens used: {response.usage.total_tokens}")
