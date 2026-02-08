"""
Agent Chat Service - Conversational AI with Tool Calling

Implements an intelligent agent that can chat with users and call tools
(fetch stock data, technical indicators, news, etc.) to answer questions.
"""

from typing import Dict, Any, List, Optional
import logging
import json
import os
from datetime import datetime

from services.agent_tools import get_tools_for_openai, execute_tool, TOOL_REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Install with: pip install openai")

# Conversation storage (in-memory for now)
CONVERSATIONS: Dict[str, List[Dict]] = {}

# System prompt for the financial advisor agent
AGENT_SYSTEM_PROMPT = """You are an expert financial advisor AI assistant with access to real-time stock market data and analysis tools.

Your role:
- Help users make informed investment decisions
- Provide clear, concise answers to financial questions
- Use available tools to fetch real-time data when needed
- Be honest about limitations and risks
- Never guarantee returns or make promises

Available tools:
- get_stock_price: Current price and daily change
- get_technical_indicators: RSI, MACD, Bollinger Bands, Moving Averages
- get_company_metrics: Financial health, valuation, profitability
- search_stock_news: Recent news articles about stocks
- compare_stocks: Side-by-side comparison of two stocks

Guidelines:
- Always use tools to get current data before answering
- Cite data sources in your responses
- Explain technical terms simply
- Provide actionable insights
- Be concise but comprehensive
- Use bullet points for clarity

When users ask about stocks:
1. Fetch relevant data using tools
2. Analyze the data
3. Provide clear recommendations with reasoning
4. Mention key risks

Example responses:
- "Let me check the current data for META..."
- "Based on the RSI of 65.2, META is approaching overbought territory..."
- "The MACD shows a bullish crossover, suggesting upward momentum..."
"""


def chat_with_agent(
    user_message: str,
    conversation_id: str,
    ticker: Optional[str] = None,
    history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Main chat function with tool calling support.
    
    Args:
        user_message: User's question/message
        conversation_id: Unique conversation ID
        ticker: Default ticker context (optional)
        history: Previous conversation history (optional)
        
    Returns:
        Dictionary with:
        - reply: AI response
        - tool_calls: List of tools called
        - conversation_id: Conversation ID
        - timestamp: Response timestamp
    """
    if not OPENAI_AVAILABLE:
        return {
            'error': 'OpenAI not available. Install: pip install openai',
            'reply': 'Sorry, the AI service is not configured properly.',
            'tool_calls': [],
            'conversation_id': conversation_id
        }
    
    try:
        # Get or create conversation
        if conversation_id not in CONVERSATIONS:
            CONVERSATIONS[conversation_id] = []
        
        conversation = CONVERSATIONS[conversation_id]
        
        # Add context about current ticker if provided
        context_message = ""
        if ticker:
            context_message = f"\n\nContext: The user is currently viewing {ticker} on the dashboard."
        
        # Build messages
        messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT + context_message}]
        
        # Add history (last 10 messages to stay within token limits)
        if history:
            messages.extend(history[-10:])
        elif conversation:
            messages.extend(conversation[-10:])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI with tools
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'error': 'OPENAI_API_KEY not set',
                'reply': 'API key not configured. Please set OPENAI_API_KEY environment variable.',
                'tool_calls': [],
                'conversation_id': conversation_id
            }
        
        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        tools = get_tools_for_openai()
        
        logger.info(f"Chat request - Model: {model}, Tools: {len(tools)}, Message: {user_message[:50]}...")
        
        # First API call - may request tool calls
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=800
        )
        
        assistant_message = response.choices[0].message
        tool_calls_made = []
        
        # Check if model wants to call tools
        if assistant_message.tool_calls:
            logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool calls")
            
            # Add assistant message with tool calls to conversation
            messages.append(assistant_message)
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Execute the tool
                tool_result = execute_tool(tool_name, tool_args)
                
                # Track tool call
                tool_calls_made.append({
                    'tool': tool_name,
                    'args': tool_args,
                    'result': tool_result
                })
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
            
            # Second API call - get final response with tool results
            final_response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            final_reply = final_response.choices[0].message.content
        else:
            # No tools needed, use initial response
            final_reply = assistant_message.content
        
        # Update conversation history
        conversation.append({"role": "user", "content": user_message})
        conversation.append({"role": "assistant", "content": final_reply})
        CONVERSATIONS[conversation_id] = conversation
        
        logger.info(f"Chat response generated - Tools used: {len(tool_calls_made)}")
        
        return {
            'reply': final_reply,
            'tool_calls': tool_calls_made,
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'model': model
        }
        
    except Exception as e:
        logger.error(f"Error in chat_with_agent: {e}")
        return {
            'error': str(e),
            'reply': f"I encountered an error: {str(e)}. Please try rephrasing your question.",
            'tool_calls': [],
            'conversation_id': conversation_id
        }


def clear_conversation(conversation_id: str) -> bool:
    """
    Clear conversation history for a specific ID.
    
    Args:
        conversation_id: Conversation ID to clear
        
    Returns:
        True if cleared, False if not found
    """
    if conversation_id in CONVERSATIONS:
        del CONVERSATIONS[conversation_id]
        logger.info(f"Cleared conversation: {conversation_id}")
        return True
    return False


def get_conversation(conversation_id: str) -> List[Dict]:
    """
    Get conversation history for a specific ID.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        List of messages or empty list
    """
    return CONVERSATIONS.get(conversation_id, [])


def get_all_conversation_ids() -> List[str]:
    """Get all active conversation IDs"""
    return list(CONVERSATIONS.keys())
