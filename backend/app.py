"""
Simple Flask backend for restaurant menu creator
Uses fal.ai alpha-image-232 for generation and editing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import fal_client
from dotenv import load_dotenv
import json

load_dotenv()
app = Flask(__name__)
CORS(app)


def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  └─ {log['message']}")


def generate_food_image(food_name, description):
    """Generate a realistic food image using fal.ai/beta-image-232."""
    prompt = f"Professional food photography of {food_name}"
    if description:
        prompt += f", {description}"
    prompt += ". High quality, appetizing, restaurant menu style, natural lighting, close-up shot, realistic"

    try:
        print(f"  Generating image with prompt: {prompt[:100]}...")
        result = fal_client.subscribe(
            "fal-ai/beta-image-232",
            arguments={
                "prompt": prompt,
                "image_size": "square",
                "num_images": 1
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = result['images'][0]['url']
        print(f"  ✓ Generated image: {image_url}")
        return image_url

    except Exception as e:
        print(f"  ✗ Error generating image for {food_name}: {e}")
        # Return a placeholder or empty string
        return ""


@app.route('/api/surprise', methods=['POST'])
def surprise_me():
    """Generate menu content from simple prompt using AI."""
    data = request.json
    user_prompt = data.get('prompt', 'a burger joint')

    # Use fal.ai text generation or simple template for now
    # For simplicity, using a basic template generator
    # In production, you'd use an LLM here

    menu_data = generate_menu_content(user_prompt)

    return jsonify(menu_data)


@app.route('/api/generate', methods=['POST'])
def generate_menu():
    """Generate menu image from menu items."""
    data = request.json
    restaurant_name = data.get('restaurantName', 'Restaurant')
    items = data.get('items', [])
    style = data.get('style', 'modern')

    print(f"Processing {len(items)} menu items...")

    # Generate images for items that don't have them
    for item in items:
        if not item.get('imageUrl'):
            print(f"Generating image for: {item['name']}")
            item['imageUrl'] = generate_food_image(item['name'], item.get('description', ''))
        else:
            print(f"Using provided image for: {item['name']}")

    # Build prompt
    prompt = build_menu_prompt(restaurant_name, items, style)

    print(f"Generating menu with prompt: {prompt[:200]}...")

    # Generate image
    result = fal_client.subscribe(
        "fal-ai/alpha-image-232/text-to-image",
        arguments={"prompt": prompt},
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    image_url = result['images'][0]['url']

    return jsonify({
        'imageUrl': image_url,
        'prompt': prompt,
        'items': items  # Return items with generated image URLs
    })


@app.route('/api/edit', methods=['POST'])
def edit_menu():
    """Edit existing menu image."""
    data = request.json
    image_url = data.get('imageUrl')
    edit_instruction = data.get('editInstruction')

    print(f"Editing menu: {edit_instruction}")

    result = fal_client.subscribe(
        "fal-ai/alpha-image-232/edit-image",
        arguments={
            "image_urls": [image_url],
            "prompt": edit_instruction,
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    edited_url = result['images'][0]['url']

    return jsonify({
        'imageUrl': edited_url
    })


def generate_menu_content(user_prompt):
    """Generate menu content from user prompt using AI."""

    prompt = f"""You are a restaurant menu creator AI. Given a description of a restaurant type or concept,
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

    try:
        # Collect all streamed content
        full_content = ""
        stream = fal_client.stream(
            "openrouter/router",
            arguments={
                "prompt": prompt,
                "model": "google/gemini-2.5-flash",
                "temperature": 1
            }
        )

        final_output = None
        for event in stream:
            # The final event has partial: False and contains the complete response
            if isinstance(event, dict) and event.get('partial') == False:
                final_output = event.get('output', '')
                break

        if not final_output:
            raise ValueError("No final output received from stream")

        print(f"Full AI response (first 200 chars): {final_output[:200]}")

        # Strip markdown code blocks if present
        json_str = final_output.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:]  # Remove ```json
        if json_str.startswith('```'):
            json_str = json_str[3:]  # Remove ```
        if json_str.endswith('```'):
            json_str = json_str[:-3]  # Remove trailing ```
        json_str = json_str.strip()

        print(f"Cleaned JSON (first 200 chars): {json_str[:200]}")

        # Parse the JSON response
        menu_data = json.loads(json_str)

        return menu_data

    except Exception as e:
        print(f"Error generating menu with AI: {e}")
        print(f"Final output received: {final_output if 'final_output' in locals() else 'None'}")
        # Fallback to a simple default
        return {
            'restaurantName': 'The Restaurant',
            'items': [
                {'category': 'Appetizers', 'name': 'Soup of the Day', 'price': 6, 'description': 'Fresh daily soup'},
                {'category': 'Main Course', 'name': 'Grilled Chicken', 'price': 16, 'description': 'Herb-marinated chicken breast'},
                {'category': 'Desserts', 'name': 'Cheesecake', 'price': 7, 'description': 'Classic New York style'},
            ]
        }


def build_menu_prompt(restaurant_name, items, style):
    """Build detailed prompt for menu generation."""

    # Style mappings
    style_descriptions = {
        'modern': 'Modern clean design, minimalist, sharp typography, high contrast',
        'vintage': 'Vintage rustic style, chalkboard aesthetic, hand-drawn feel, warm colors',
        'elegant': 'Elegant upscale design, sophisticated fonts, gold accents, luxury feel',
        'casual': 'Casual friendly design, bright colors, fun fonts, approachable layout',
    }

    style_desc = style_descriptions.get(style, style_descriptions['modern'])

    # Group items by category
    categories = {}
    for item in items:
        cat = item.get('category', 'Items')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    # Build prompt
    prompt = f"Professional restaurant menu for '{restaurant_name}' with food photography layout.\n\n"

    for category, cat_items in categories.items():
        prompt += f"{category.upper()}:\n"
        for item in cat_items:
            name = item.get('name', '')
            price = item.get('price', 0)
            desc = item.get('description', '')
            has_image = bool(item.get('imageUrl'))

            prompt += f"- {name} ${price}"
            if desc:
                prompt += f" - {desc}"
            if has_image:
                prompt += " [with food photo]"
            prompt += "\n"
        prompt += "\n"

    prompt += f"\n{style_desc}. Include space for food photographs next to items. Sharp, crisp, highly readable text. Clear prices. Professional layout with image placeholders."

    return prompt


if __name__ == '__main__':
    app.run(debug=True, port=5001)
