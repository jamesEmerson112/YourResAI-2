# Restaurant Menu Creator - Complete Package

A full-stack web application that uses AI to create beautiful restaurant menus with automatic content generation and image editing capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)

## Overview

This application helps create professional restaurant menus using AI-powered image generation and editing. It features both an automated "Surprise Me" mode that generates complete menus from simple prompts, and a manual mode for full control over menu creation.

## Features

### Core Features

- **Surprise Me Mode**: Enter a simple prompt (e.g., "burger joint") and automatically generate restaurant name, menu items, categories, prices, and descriptions
- **Manual Mode**: Full control to add restaurant name, select style, and add menu items one by one
- **AI Image Generation**: Generates professional menu layouts using fal.ai's alpha-image-232 model
- **Style Selection**: Choose from 4 different styles:
  - Modern: Clean, minimalist design with sharp typography
  - Vintage: Rustic chalkboard aesthetic with warm colors
  - Elegant: Sophisticated with gold accents and luxury feel
  - Casual: Bright colors with fun, approachable layout
- **Menu Editing**: Refine generated menus with natural language instructions (e.g., "Make text larger", "Fix the price of Bruschetta to $8")
- **Download**: Export your menu as a high-quality PNG image

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │ ◄─────► │    Flask     │ ◄─────► │  fal.ai API │
│  Frontend   │  HTTP   │   Backend    │  REST   │ (AI Models) │
│  Port 3000  │         │  Port 5001   │         └─────────────┘
└─────────────┘         └──────────────┘
```

- **Frontend**: React SPA with split-panel UI (form on left, preview on right)
- **Backend**: Flask REST API handling AI model interactions
- **AI Services**:
  - `beta-image-232`: Food image generation
  - `alpha-image-232/text-to-image`: Menu layout generation
  - `alpha-image-232/edit-image`: Menu refinement
  - `openrouter/router` (Gemini 2.5 Flash): Content generation

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 14+** and **npm** (for frontend)
- **fal.ai API Key** (required)

### Getting a fal.ai API Key

1. Sign up at [fal.ai](https://fal.ai)
2. Navigate to your dashboard
3. Generate an API key
4. Keep this key secure - you'll need it for setup

## Installation & Setup

### Step 1: Extract the Package

```bash
tar -xzf menu-creator.tar.gz
cd menu-creator
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "FAL_KEY=your_fal_api_key_here" > .env
```

**Important**: Replace `your_fal_api_key_here` with your actual fal.ai API key.

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd ../frontend

# Install dependencies
npm install
```

### Step 4: Start the Application

You'll need two terminal windows:

**Terminal 1 - Backend:**
```bash
cd menu-creator/backend
source venv/bin/activate  # If not already activated
python app.py
```

Backend will start on: `http://localhost:5001`

**Terminal 2 - Frontend:**
```bash
cd menu-creator/frontend
npm start
```

Frontend will start on: `http://localhost:3000`

The browser should automatically open to `http://localhost:3000`. If not, navigate there manually.

## Usage Guide

### Quick Start: Surprise Me Mode

1. Open the application at `http://localhost:3000`
2. In the "Surprise Me" section (top left), enter a restaurant concept:
   - "I want to start a burger joint"
   - "Italian pizza place"
   - "Cozy coffee shop"
3. Click **"Generate Everything"**
4. Wait for AI to generate restaurant name and complete menu
5. Review the generated items and adjust if needed
6. Click **"Generate Menu Image"**
7. Wait for the menu to be generated (appears on right side)
8. Click **"Download Menu"** to save

### Manual Mode

1. Enter a restaurant name in the "Restaurant Name" field
2. Select a style from the dropdown (Modern/Vintage/Elegant/Casual)
3. For each menu item, fill in:
   - Category (e.g., "Appetizers", "Main Course")
   - Item name
   - Price (numbers only, no $ sign)
   - Description (optional)
4. Click **"Add Item"** for each item
5. Once all items are added, click **"Generate Menu Image"**
6. Download or edit as needed

### Editing Your Menu

After generating a menu:

1. Scroll to the "Edit Menu" section (below the preview)
2. Enter natural language instructions:
   - "Make the text larger"
   - "Change the background to dark blue"
   - "Fix the price of Bruschetta to $8"
   - "Add more spacing between items"
3. Click **"Apply Edit"**
4. Wait for the edited version to appear
5. Repeat as needed

## API Documentation

### Base URL
```
http://localhost:5001/api
```

### Endpoints

#### 1. POST `/api/surprise`

Generate menu content from a simple prompt.

**Request:**
```json
{
  "prompt": "burger joint"
}
```

**Response:**
```json
{
  "restaurantName": "The Burger Joint",
  "items": [
    {
      "category": "Main Course",
      "name": "Classic Burger",
      "price": 12,
      "description": "Juicy beef patty with lettuce and tomato"
    },
    ...
  ]
}
```

#### 2. POST `/api/generate`

Generate menu image from items.

**Request:**
```json
{
  "restaurantName": "The Burger Joint",
  "style": "modern",
  "items": [
    {
      "category": "Main Course",
      "name": "Classic Burger",
      "price": 12,
      "description": "Juicy beef patty"
    }
  ]
}
```

**Response:**
```json
{
  "imageUrl": "https://fal.media/files/...",
  "prompt": "Professional restaurant menu for...",
  "items": [...]
}
```

#### 3. POST `/api/edit`

Edit an existing menu image.

**Request:**
```json
{
  "imageUrl": "https://fal.media/files/...",
  "editInstruction": "Make the text larger"
}
```

**Response:**
```json
{
  "imageUrl": "https://fal.media/files/..."
}
```

## Project Structure

```
menu-creator/
├── backend/
│   ├── app.py                 # Flask server with API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # API keys (create this - not included)
│   └── output.txt            # Log file (generated)
│
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # App styling
│   │   ├── index.js          # React entry point
│   │   ├── index.css         # Global styles
│   │   └── components/
│   │       ├── MenuForm.js      # Left panel: input form
│   │       ├── MenuForm.css     # Form styling
│   │       ├── MenuPreview.js   # Right panel: preview & download
│   │       └── MenuPreview.css  # Preview styling
│   ├── package.json          # Node dependencies and scripts
│   └── package-lock.json     # Locked dependency versions
│
├── README.md                 # Quick reference guide
├── QUICKSTART.md            # Detailed quick start guide
└── PACKAGE_README.md        # This file - complete documentation
```

## Technologies Used

### Frontend
- **React 18.2.0**: UI framework
- **React Scripts 5.0.1**: Build tooling
- **Fetch API**: HTTP requests to backend

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **fal-client**: Python SDK for fal.ai API
- **python-dotenv**: Environment variable management

### AI Models (via fal.ai)
- **beta-image-232**: High-quality food photography generation
- **alpha-image-232/text-to-image**: Menu layout generation
- **alpha-image-232/edit-image**: Menu image editing
- **openrouter/router** (Gemini 2.5 Flash): Natural language content generation

## Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'flask'`**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Problem: `Error: FAL_KEY not found`**
```bash
# Create .env file in backend directory
echo "FAL_KEY=your_actual_key" > .env
```

**Problem: Backend runs on wrong port**
- Check `app.py` line 259: `app.run(debug=True, port=5001)`
- Frontend expects backend on port 5001 (see `frontend/package.json` proxy setting)

### Frontend Issues

**Problem: `npm: command not found`**
- Install Node.js from [nodejs.org](https://nodejs.org)

**Problem: `Failed to compile` errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem: Cannot connect to backend**
- Ensure backend is running on port 5001
- Check `frontend/package.json` has: `"proxy": "http://localhost:5001"`
- Check browser console for CORS errors

### API Issues

**Problem: "API key invalid" or 401 errors**
- Verify your fal.ai API key is correct in `.env`
- Check key has proper permissions on fal.ai dashboard

**Problem: Slow generation**
- AI image generation can take 30-60 seconds
- Check terminal logs for progress updates
- Network speed affects download times for generated images

**Problem: Generated images not appearing**
- Check browser console for errors
- Verify image URLs are accessible (they're temporary fal.ai URLs)
- Check if ad blockers are interfering

### General Tips

1. **Always check both terminal windows** for error messages
2. **Browser DevTools** (F12) shows frontend errors and network requests
3. **Backend terminal** shows API calls and AI generation progress
4. **Clear browser cache** if you see old menu images stuck
5. **Restart both servers** if something seems broken

## Configuration Options

### Backend Port
Edit `backend/app.py` line 259:
```python
app.run(debug=True, port=5001)  # Change 5001 to your desired port
```

Don't forget to update the proxy in `frontend/package.json`:
```json
"proxy": "http://localhost:YOUR_PORT"
```

### Frontend Port
Create `frontend/.env` file:
```
PORT=3000  # Change to your desired port
```

### AI Model Parameters

In `backend/app.py`, you can adjust:

**Image generation (line 32-37)**:
```python
"prompt": prompt,
"image_size": "square",  # Options: square, portrait, landscape
"num_images": 1          # Number of variations
```

**Content generation (line 166)**:
```python
"model": "google/gemini-2.5-flash",
"temperature": 1  # Creativity level (0-2)
```

## License & Credits

This project uses:
- fal.ai for AI image generation and editing
- Google Gemini 2.5 Flash (via OpenRouter) for content generation

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review terminal logs for error messages
3. Verify all prerequisites are installed correctly
4. Ensure API keys are valid and have proper permissions

---

**Created with**: React + Flask + fal.ai
**Version**: 1.0.0
**Last Updated**: November 2024
