"""
NVIDIA Nemotron client wrapper for menu generation
Handles API calls, retry logic, validation, and error handling
"""

from openai import OpenAI, OpenAIError, RateLimitError, APIError
from typing import Dict, Any, Tuple
import time
import json
import os
import re


class NvidiaClient:
    """Lightweight NVIDIA Nemotron client for restaurant menu generation"""

    def __init__(self):
        """Initialize NVIDIA client with OpenAI SDK"""
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"

        # Default parameters matching nemotron reference
        self.default_temperature = 0.6
        self.default_top_p = 0.95
        self.default_max_tokens = 32768

        # Retry configuration for rate limiting
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _extract_reasoning(self, content: str) -> Tuple[str, str]:
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

    def generate_menu_json(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate restaurant menu JSON from user prompt.

        Args:
            user_prompt: User's description of restaurant concept

        Returns:
            Dictionary with restaurantName and items array

        Raises:
            Exception: If all retry attempts fail
        """
        prompt = self._build_menu_prompt(user_prompt)

        # Attempt API call with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.default_temperature,
                    top_p=self.default_top_p,
                    max_tokens=self.default_max_tokens
                )

                content = response.choices[0].message.content
                print(f"NVIDIA API response (first 200 chars): {content[:200]}")

                # Extract reasoning from response (if present)
                reasoning, final_answer = self._extract_reasoning(content)

                if reasoning:
                    print(f"🧠 Reasoning process (first 150 chars): {reasoning[:150]}...")
                    print(f"📄 Final answer (first 200 chars): {final_answer[:200]}")

                # Validate and parse only the final answer (without reasoning tags)
                if self._validate_response(final_answer):
                    menu_data = self._parse_json_response(final_answer)
                    print(f"✓ Successfully generated menu: {menu_data.get('restaurantName', 'Unknown')}")
                    return menu_data
                else:
                    print("⚠ Response validation failed, using fallback")
                    return self._get_fallback_menu()

            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"⚠ Rate limit hit. Retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Rate limit exceeded after {self.max_retries} attempts")
                    return self._get_fallback_menu()

            except APIError as e:
                print(f"✗ NVIDIA API error: {e}")
                if attempt < self.max_retries - 1:
                    print(f"  Retrying... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    print(f"  Failed after {self.max_retries} attempts, using fallback")
                    return self._get_fallback_menu()

            except OpenAIError as e:
                print(f"✗ OpenAI SDK error: {e}")
                return self._get_fallback_menu()

            except Exception as e:
                print(f"✗ Unexpected error in menu generation: {e}")
                return self._get_fallback_menu()

        # Should not reach here, but safety fallback
        return self._get_fallback_menu()

    def _build_menu_prompt(self, user_prompt: str) -> str:
        """Build the prompt for menu generation"""
        return f"""You are a restaurant menu creator AI. Given a description of a restaurant type or concept,
generate a complete restaurant menu with a creative name, menu items organized by category, with prices and descriptions.

User request: {user_prompt}

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just raw JSON):
{{
    "restaurantName": "Creative Restaurant Name",
    "items": [
        {{"category": "Category Name", "name": "Item Name", "price": 12, "description": "Brief description"}},
        ...
    ]
}}

Guidelines:
- Create 3-6 menu items total
- Use appropriate categories (Appetizers, Main Course, Sides, Desserts, Drinks, etc.)
- Prices should be realistic numbers (no $ symbol, just the number)
- Descriptions should be brief (under 15 words)
- Make the restaurant name creative and fitting to the concept"""

    def _validate_response(self, content: str) -> bool:
        """
        Validate that response has expected structure.

        Args:
            content: Raw response content from API

        Returns:
            True if response is valid, False otherwise
        """
        if not content or len(content.strip()) == 0:
            print("  Validation failed: Empty response")
            return False

        # Try to parse as JSON
        try:
            cleaned = self._clean_json(content)
            data = json.loads(cleaned)

            # Check required fields
            if 'restaurantName' not in data:
                print("  Validation failed: Missing 'restaurantName' field")
                return False

            if 'items' not in data or not isinstance(data['items'], list):
                print("  Validation failed: Missing or invalid 'items' field")
                return False

            if len(data['items']) == 0:
                print("  Validation failed: No menu items")
                return False

            # Validate at least one item has required fields
            first_item = data['items'][0]
            required_fields = ['category', 'name', 'price']
            if not all(field in first_item for field in required_fields):
                print(f"  Validation failed: Menu item missing required fields")
                return False

            return True

        except json.JSONDecodeError as e:
            print(f"  Validation failed: Invalid JSON - {e}")
            return False
        except Exception as e:
            print(f"  Validation failed: {e}")
            return False

    def _clean_json(self, content: str) -> str:
        """
        Clean markdown code blocks and formatting from JSON response.

        Args:
            content: Raw response content

        Returns:
            Cleaned JSON string
        """
        json_str = content.strip()

        # Remove markdown code blocks
        if json_str.startswith('```json'):
            json_str = json_str[7:]
        if json_str.startswith('```'):
            json_str = json_str[3:]
        if json_str.endswith('```'):
            json_str = json_str[:-3]

        return json_str.strip()

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse and return validated menu data.

        Args:
            content: Response content to parse

        Returns:
            Parsed menu dictionary

        Raises:
            json.JSONDecodeError: If parsing fails
        """
        cleaned = self._clean_json(content)
        return json.loads(cleaned)

    def _get_fallback_menu(self) -> Dict[str, Any]:
        """
        Return a basic fallback menu when API fails.

        Returns:
            Default menu dictionary
        """
        return {
            'restaurantName': 'The Restaurant',
            'items': [
                {
                    'category': 'Appetizers',
                    'name': 'Soup of the Day',
                    'price': 6,
                    'description': 'Fresh daily soup'
                },
                {
                    'category': 'Main Course',
                    'name': 'Grilled Chicken',
                    'price': 16,
                    'description': 'Herb-marinated chicken breast'
                },
                {
                    'category': 'Desserts',
                    'name': 'Cheesecake',
                    'price': 7,
                    'description': 'Classic New York style'
                }
            ]
        }
