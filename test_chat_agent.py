"""
Quick test script for chat agent functionality
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test 1: Check API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
print("=== Environment Check ===")
print(f"OpenAI API Key: {'✓ Set' if api_key else '✗ NOT SET'}")
if api_key:
    print(f"Key starts with: {api_key[:20]}...")

# Test 2: Check OpenAI package
try:
    import openai
    print(f"OpenAI package: ✓ Installed (v{openai.__version__})")
except ImportError as e:
    print(f"OpenAI package: ✗ NOT INSTALLED - {e}")
    exit(1)

# Test 3: Check services
try:
    from services.agent_tools import get_tools_for_openai, execute_tool, TOOL_REGISTRY
    print(f"Agent Tools: ✓ Loaded ({len(TOOL_REGISTRY)} tools registered)")
    
    # List tools
    print("\n=== Registered Tools ===")
    for i, (tool_name, tool_info) in enumerate(TOOL_REGISTRY.items(), 1):
        print(f"{i}. {tool_name}: {tool_info['description']}")
    
except ImportError as e:
    print(f"Agent Tools: ✗ IMPORT ERROR - {e}")
    exit(1)

# Test 4: Test a tool execution
print("\n=== Tool Execution Test ===")
try:
    result = execute_tool('get_stock_price', {'ticker': 'META'})
    print(f"✓ get_stock_price('META') returned:")
    for key, value in result.items():
        print(f"  - {key}: {value}")
except Exception as e:
    print(f"✗ Tool execution failed: {e}")

# Test 5: Test OpenAI API connection
print("\n=== OpenAI API Connection Test ===")
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Simple completion test
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test successful' if you receive this"}],
        max_tokens=10
    )
    print(f"✓ API Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ OpenAI API test failed: {e}")

# Test 6: Test chat service
print("\n=== Chat Service Test ===")
try:
    from services.agent_chat_service import chat_with_agent
    
    response = chat_with_agent(
        user_message="What's the current price of META?",
        conversation_id="test_123",
        ticker="META",
        history=[]
    )
    
    print(f"✓ Chat Agent Response:")
    print(f"  Message: {response['reply'][:200]}...")
    print(f"  Tools Called: {len(response.get('tool_calls', []))}")
    if response.get('tool_calls'):
        for tc in response['tool_calls']:
            print(f"    - {tc['name']}({tc['arguments']})")
    
except Exception as e:
    print(f"✗ Chat service test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
