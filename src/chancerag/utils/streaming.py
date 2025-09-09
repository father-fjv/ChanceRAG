"""Streaming response utilities."""

import logging
import asyncio
from typing import AsyncGenerator, Any, Optional, Union
from langchain.schema import BaseMessage

logger = logging.getLogger(__name__)


async def stream_response(
    response: Union[AsyncGenerator, Any], 
    return_output: bool = False
) -> Optional[str]:
    """
    Stream response from LLM and optionally return final output.
    
    Args:
        response: LLM response (streaming or regular)
        return_output: Whether to return the final output
        
    Returns:
        Final output if return_output is True, otherwise None
    """
    try:
        full_output = ""
        
        if hasattr(response, '__aiter__'):
            # Handle async generator (streaming response)
            async for chunk in response:
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    print(content, end='', flush=True)
                    full_output += content
                elif isinstance(chunk, str):
                    print(chunk, end='', flush=True)
                    full_output += chunk
                else:
                    # Handle other chunk types
                    chunk_str = str(chunk)
                    print(chunk_str, end='', flush=True)
                    full_output += chunk_str
                
                # Small delay for better UX
                await asyncio.sleep(0.01)
        else:
            # Handle regular response
            if hasattr(response, 'content'):
                content = response.content
                print(content, end='', flush=True)
                full_output = content
            else:
                content = str(response)
                print(content, end='', flush=True)
                full_output = content
        
        print()  # New line after streaming
        
        if return_output:
            return full_output
        return None
        
    except Exception as e:
        logger.error(f"Error in streaming response: {e}")
        print(f"Error: {e}")
        return None if not return_output else ""


async def stream_chat_response(
    messages: list[BaseMessage],
    llm: Any,
    return_output: bool = False
) -> Optional[str]:
    """
    Stream chat response from LLM.
    
    Args:
        messages: List of chat messages
        llm: Language model instance
        return_output: Whether to return the final output
        
    Returns:
        Final output if return_output is True, otherwise None
    """
    try:
        if hasattr(llm, 'astream'):
            # Use async streaming if available
            response = llm.astream(messages)
            return await stream_response(response, return_output)
        elif hasattr(llm, 'stream'):
            # Use sync streaming
            response = llm.stream(messages)
            return await stream_response(response, return_output)
        else:
            # Fallback to regular invoke
            response = await llm.ainvoke(messages) if hasattr(llm, 'ainvoke') else llm.invoke(messages)
            return await stream_response(response, return_output)
            
    except Exception as e:
        logger.error(f"Error in streaming chat response: {e}")
        print(f"Error: {e}")
        return None if not return_output else ""


def print_streaming_header():
    """Print streaming response header."""
    print("\n" + "="*50)
    print("🤖 AI 답변")
    print("="*50)


def print_streaming_footer():
    """Print streaming response footer."""
    print("\n" + "="*50)
    print("답변 완료")
    print("="*50 + "\n")
