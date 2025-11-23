from openai import OpenAI
from typing import List, Optional, Dict, Any
import re
from src.config import settings
from src.models.schemas import Message, Tool


class NemotronClient:
    """Client wrapper for NVIDIA Nemotron API using OpenAI SDK"""

    def __init__(self):
        """Initialize the OpenAI client with NVIDIA credentials"""
        self.client = OpenAI(
            base_url=settings.nvidia_base_url,
            api_key=settings.nvidia_api_key
        )
        self.model_name = settings.model_name

    def _prepare_system_prompt(self, reasoning_mode: bool = True) -> str:
        """
        Prepare system prompt based on reasoning mode.

        Args:
            reasoning_mode: If False, adds /no_think to disable reasoning

        Returns:
            System prompt string
        """
        if reasoning_mode:
            return ""  # Default behavior is reasoning ON
        else:
            return "/no_think"  # Disable reasoning mode

    def _extract_reasoning(self, content: str) -> tuple[str, str]:
        """
        Extract reasoning process and final answer from response.

        The model wraps reasoning in <think>...</think> tags.

        Args:
            content: Full response content

        Returns:
            Tuple of (reasoning_process, final_answer)
        """
        # Pattern to extract thinking process
        think_pattern = r'<think>(.*?)</think>'
        thinking_match = re.search(think_pattern, content, re.DOTALL)

        if thinking_match:
            reasoning = thinking_match.group(1).strip()
            # Remove thinking tags from content to get final answer
            final_answer = re.sub(think_pattern, '', content, flags=re.DOTALL).strip()
            return reasoning, final_answer
        else:
            # No reasoning tags found, entire content is the answer
            return "", content

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.6,
        top_p: float = 0.95,
        max_tokens: int = 32768,
        reasoning_mode: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Nemotron.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            reasoning_mode: Enable reasoning with thinking process
            stream: Enable streaming response

        Returns:
            API response with content and metadata
        """
        # Convert messages to OpenAI format
        formatted_messages = []

        # Add system prompt if needed
        system_prompt = self._prepare_system_prompt(reasoning_mode)
        if system_prompt or any(msg.role == "system" for msg in messages):
            # Find existing system message or create new one
            system_msg = next((msg for msg in messages if msg.role == "system"), None)
            if system_msg:
                formatted_messages.append({
                    "role": "system",
                    "content": system_msg.content + ("\n" + system_prompt if system_prompt else "")
                })
                # Add remaining non-system messages
                formatted_messages.extend([
                    {"role": msg.role.value, "content": msg.content}
                    for msg in messages if msg.role != "system"
                ])
            else:
                formatted_messages.append({"role": "system", "content": system_prompt})
                formatted_messages.extend([
                    {"role": msg.role.value, "content": msg.content}
                    for msg in messages
                ])
        else:
            formatted_messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]

        # Make API call
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream
        )

        # Parse response
        if not stream:
            content = response.choices[0].message.content
            reasoning, final_answer = self._extract_reasoning(content)

            return {
                "id": response.id,
                "model": response.model,
                "created": response.created,
                "content": final_answer,
                "reasoning": reasoning if reasoning else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }
        else:
            return response

    def reasoning_task(
        self,
        prompt: str,
        task_type: str = "general",
        temperature: float = 0.6,
        top_p: float = 0.95,
        max_tokens: int = 32768
    ) -> Dict[str, Any]:
        """
        Execute a reasoning task with explicit thinking process.

        Args:
            prompt: The reasoning task prompt
            task_type: Type of task (math, code, science, general)
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Response with reasoning process and final answer
        """
        # Craft system prompt based on task type
        task_prompts = {
            "math": "You are a mathematical reasoning expert. Think through the problem step by step.",
            "code": "You are a code reasoning expert. Analyze the problem and provide a detailed solution.",
            "science": "You are a scientific reasoning expert. Explain the concepts and reasoning clearly.",
            "general": "Think through this problem step by step and provide a detailed explanation."
        }

        system_prompt = task_prompts.get(task_type, task_prompts["general"])

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=prompt)
        ]

        response = self.chat(
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            reasoning_mode=True
        )

        return {
            "reasoning_process": response.get("reasoning", ""),
            "final_answer": response["content"],
            "task_type": task_type,
            "usage": response.get("usage")
        }

    def tool_call(
        self,
        messages: List[Message],
        tools: List[Tool],
        temperature: float = 0.6,
        top_p: float = 0.95,
        max_tokens: int = 32768
    ) -> Dict[str, Any]:
        """
        Execute tool calling with function definitions.

        Args:
            messages: Conversation messages
            tools: Available tool definitions
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Response with tool calls or content
        """
        # Convert messages and tools to OpenAI format
        formatted_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        formatted_tools = [
            {
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": tool.function.parameters
                }
            }
            for tool in tools
        ]

        # Make API call with tools
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages,
            tools=formatted_tools,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )

        message = response.choices[0].message

        result = {
            "content": message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        }

        # Check if tool calls were made
        if hasattr(message, 'tool_calls') and message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]

        return result
