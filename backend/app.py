"""
Simple Flask backend for restaurant menu creator
Uses fal.ai beta-image-232 for generation and editing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import fal_client
from dotenv import load_dotenv
from nvidia_client import NvidiaClient
import threading
import uuid
from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize NVIDIA client wrapper
nvidia_client = NvidiaClient()

# In-memory storage for variant generation sessions
variant_sessions = {}


def generate_menu_variant_visual(restaurant_name, items, style, variant_id):
    """
    Generate visual variant using SAME menu data with different style.

    Args:
        restaurant_name: Restaurant name
        items: Menu items (with imageUrl already generated)
        style: Visual style (elegant, modern, vintage, casual)
        variant_id: Variant number (1, 2, or 3)

    Returns:
        Complete menu data with image URL
    """
    try:
        print(f"\n🎨 Generating Variant {variant_id} with '{style}' style")

        # Collect food image URLs
        food_image_urls = [item['imageUrl'] for item in items if item.get('imageUrl')]

        print(f"  Using {len(food_image_urls)} existing food images")

        # Generate menu composition with specified style
        if food_image_urls:
            prompt = build_menu_prompt_with_images(restaurant_name, items, style)
            print(f"  Composing menu with style: {style}")
            result = fal_client.subscribe(
                "fal-ai/beta-image-232/edit",
                arguments={
                    "image_urls": food_image_urls,
                    "prompt": prompt,
                },
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            menu_image_url = result['images'][0]['url']
        else:
            # Fallback to text-only
            prompt = build_menu_prompt(restaurant_name, items, style)
            result = fal_client.subscribe(
                "fal-ai/beta-image-232/text-to-image",
                arguments={"prompt": prompt},
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            menu_image_url = result['images'][0]['url']

        print(f"  ✓ Variant {variant_id} complete with '{style}' style!")

        return {
            'id': variant_id,
            'restaurantName': restaurant_name,
            'items': items,
            'imageUrl': menu_image_url,
            'prompt': prompt,
            'style': style,
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"  ✗ Error generating variant {variant_id}: {e}")
        return {
            'id': variant_id,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def generate_variants_background(session_id, restaurant_name, items, styles):
    """
    Background thread function to generate visual variants 2 and 3.

    Args:
        session_id: Unique session identifier
        restaurant_name: Restaurant name from menu data
        items: Menu items with food images already generated
        styles: List of 3 styles [style1, style2, style3]
    """
    print(f"\n🔄 Background generation started for session {session_id}")

    # Generate variant 2 with different style
    variant2 = generate_menu_variant_visual(restaurant_name, items, styles[1], 2)
    variant_sessions[session_id]['variants'][2] = variant2
    print(f"✓ Variant 2 complete and stored")

    # Generate variant 3 with different style
    variant3 = generate_menu_variant_visual(restaurant_name, items, styles[2], 3)
    variant_sessions[session_id]['variants'][3] = variant3
    print(f"✓ Variant 3 complete and stored")

    print(f"✓ Background generation complete for session {session_id}")


@app.route('/api/generate-variants', methods=['POST'])
def generate_variants():
    """
    Generate 3 menu variants with progressive loading.
    Same menu content, but 3 different visual styles.
    Returns variant 1 immediately, generates 2 & 3 in background.
    """
    data = request.json
    user_prompt = data.get('prompt', 'a burger joint')

    # Create unique session ID
    session_id = str(uuid.uuid4())

    # Define visual styles for the 3 variants
    styles = ['elegant', 'modern', 'vintage']

    print(f"\n{'='*60}")
    print(f"NEW VARIANT GENERATION REQUEST")
    print(f"Session ID: {session_id}")
    print(f"User Prompt: {user_prompt}")
    print(f"{'='*60}")

    try:
        # Step 1: Generate menu JSON ONCE using NVIDIA
        print(f"\n📋 Step 1/3: Generating menu data...")
        menu_data = nvidia_client.generate_menu_json(user_prompt)
        restaurant_name = menu_data.get('restaurantName', 'Restaurant')
        items = menu_data.get('items', [])
        print(f"  ✓ Generated '{restaurant_name}' with {len(items)} items")

        # Step 2: Generate food images ONCE for all variants
        print(f"\n🖼️  Step 2/3: Generating {len(items)} food images...")
        for idx, item in enumerate(items):
            print(f"    Generating image {idx+1}/{len(items)}: {item['name']}")
            item['imageUrl'] = generate_food_image(item['name'], item.get('description', ''))

        food_image_count = len([i for i in items if i.get('imageUrl')])
        print(f"  ✓ Generated {food_image_count} food images")

        # Initialize session storage
        variant_sessions[session_id] = {
            'user_prompt': user_prompt,
            'restaurant_name': restaurant_name,
            'items': items,
            'created_at': datetime.now().isoformat(),
            'variants': {
                1: {'status': 'generating'},
                2: {'status': 'pending'},
                3: {'status': 'pending'}
            }
        }

        # Step 3a: Generate variant 1 immediately (elegant style)
        print(f"\n🎨 Step 3/3: Generating variant 1...")
        variant1 = generate_menu_variant_visual(restaurant_name, items, styles[0], 1)
        variant_sessions[session_id]['variants'][1] = variant1

        # Step 3b: Start background thread for variants 2 & 3 (modern and vintage styles)
        thread = threading.Thread(
            target=generate_variants_background,
            args=(session_id, restaurant_name, items, styles)
        )
        thread.daemon = True
        thread.start()

        print(f"\n✓ Variant 1 ready, variants 2 & 3 generating in background")

        # Return variant 1 immediately with session ID for polling
        return jsonify({
            'sessionId': session_id,
            'variant1': variant1,
            'variant2': {'status': 'generating'},
            'variant3': {'status': 'generating'}
        })

    except Exception as e:
        print(f"\n✗ Error in variant generation: {e}")
        return jsonify({
            'error': str(e),
            'sessionId': session_id
        }), 500


@app.route('/api/check-variant-status/<session_id>', methods=['GET'])
def check_variant_status(session_id):
    """
    Check status of background variant generation.

    Args:
        session_id: Session identifier from /api/generate-variants

    Returns:
        Current status of all variants
    """
    if session_id not in variant_sessions:
        return jsonify({'error': 'Session not found'}), 404

    session = variant_sessions[session_id]

    return jsonify({
        'sessionId': session_id,
        'variant1': session['variants'][1],
        'variant2': session['variants'][2],
        'variant3': session['variants'][3],
        'allReady': all(
            v.get('status') == 'ready'
            for v in session['variants'].values()
        )
    })


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
    """Generate menu image from menu items using FLUX.2 multi-image editing."""
    data = request.json
    restaurant_name = data.get('restaurantName', 'Restaurant')
    items = data.get('items', [])
    style = data.get('style', 'modern')

    print(f"Processing {len(items)} menu items...")

    # Generate images for items that don't have them
    food_image_urls = []
    for item in items:
        if not item.get('imageUrl'):
            print(f"Generating image for: {item['name']}")
            item['imageUrl'] = generate_food_image(item['name'], item.get('description', ''))
        else:
            print(f"Using provided image for: {item['name']}")

        # Collect image URLs for items that have them
        if item.get('imageUrl'):
            food_image_urls.append(item['imageUrl'])

    # Check if we have any images to work with
    if not food_image_urls:
        print("⚠️ No food images available, falling back to text-only generation")
        prompt = build_menu_prompt(restaurant_name, items, style)
        print(f"Generating menu with text-only prompt: {prompt[:200]}...")

        result = fal_client.subscribe(
            "fal-ai/beta-image-232/text-to-image",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        image_url = result['images'][0]['url']
    else:
        # Use FLUX.2 multi-image editing with explicit image references
        print(f"🎨 Using FLUX.2 multi-image editing with {len(food_image_urls)} food images")
        prompt = build_menu_prompt_with_images(restaurant_name, items, style)

        print(f"Generating menu with multi-image prompt: {prompt[:200]}...")
        print(f"Food image URLs: {food_image_urls[:3]}..." if len(food_image_urls) > 3 else f"Food image URLs: {food_image_urls}")

        result = fal_client.subscribe(
            "fal-ai/beta-image-232/edit",
            arguments={
                "image_urls": food_image_urls,
                "prompt": prompt,
            },
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
        "fal-ai/beta-image-232/edit",
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
    """Generate menu content from user prompt using NVIDIA client."""
    try:
        return nvidia_client.generate_menu_json(user_prompt)
    except Exception as e:
        print(f"✗ Error in menu generation: {e}")
        # Client wrapper already handles fallback, but safety catch
        return {
            'restaurantName': 'The Restaurant',
            'items': [
                {'category': 'Appetizers', 'name': 'Soup of the Day', 'price': 6, 'description': 'Fresh daily soup'},
                {'category': 'Main Course', 'name': 'Grilled Chicken', 'price': 16, 'description': 'Herb-marinated chicken breast'},
                {'category': 'Desserts', 'name': 'Cheesecake', 'price': 7, 'description': 'Classic New York style'},
            ]
        }


def build_menu_prompt(restaurant_name, items, style):
    """Build detailed prompt for menu generation (legacy text-only method)."""

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


def build_menu_prompt_with_images(restaurant_name, items, style):
    """Build FLUX.2 multi-image prompt using explicit image references."""

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

    # Build prompt with explicit image references (1-based indexing)
    prompt = f"Professional restaurant menu layout for '{restaurant_name}'.\n\n"

    image_index = 1
    for category, cat_items in categories.items():
        prompt += f"{category.upper()}:\n"
        for item in cat_items:
            name = item.get('name', '')
            price = item.get('price', 0)
            has_image = bool(item.get('imageUrl'))

            if has_image:
                # Use explicit image reference for FLUX.2 (name and price only)
                prompt += f"- Place image {image_index} ({name}, ${price})\n"
                image_index += 1
            else:
                # Text-only item
                prompt += f"- {name} ${price}\n"
        prompt += "\n"

    prompt += f"\n{style_desc}. Arrange food photographs elegantly with their names and prices. Sharp, crisp, highly readable text. Professional layout with proper spacing between items."

    return prompt


if __name__ == '__main__':
    app.run(debug=True, port=5001)
