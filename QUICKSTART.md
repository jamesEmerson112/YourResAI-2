# Restaurant Menu Creator - Quick Start

## ✅ What's Built

A simple web app with:
- **Frontend**: React (clean, minimal UI)
- **Backend**: Flask/Python
- **AI**: fal.ai alpha-image-232 models

## 🎯 Features

### 1. Surprise Me ✨
User types: "I want to start a burger joint"
→ App generates: Restaurant name + full menu with items, prices, descriptions

### 2. Manual Mode 📝
- Add restaurant name
- Choose style (Modern/Vintage/Elegant/Casual)
- Add menu items one by one
- Full control over everything

### 3. Generation 🖼️
- Generates beautiful menu image using alpha-image-232/text-to-image
- Applies selected style

### 4. Editing ✏️
- Click "Edit Menu"
- Type instructions like "Make text larger" or "Fix Bruschetta price to $8"
- Uses alpha-image-232/edit-image

### 5. Download 📥
- Save menu as PNG

## 🚀 How to Run

### Backend:
```bash
cd /Users/alazarshenkute/Projects/fal-beyond
source venv/bin/activate
cd menu-creator/backend
python app.py
```
Runs on: http://localhost:5000

### Frontend:
```bash
cd /Users/alazarshenkute/Projects/fal-beyond/menu-creator/frontend
npm start
```
Runs on: http://localhost:3000

## 📁 Project Structure

```
menu-creator/
├── backend/
│   ├── app.py           # Flask API
│   ├── .env             # FAL_KEY
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.js              # Main app
    │   ├── components/
    │   │   ├── MenuForm.js     # Left panel - input form
    │   │   └── MenuPreview.js  # Right panel - preview
    │   └── *.css               # Styling
    └── package.json
```

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────┐
│         Restaurant Menu Creator                  │
├──────────────────┬──────────────────────────────┤
│  LEFT PANEL      │  RIGHT PANEL                  │
│                  │                               │
│  ✨ Surprise Me  │  📋 Preview                   │
│  [Input]         │                               │
│  [Generate]      │  [Generated Image]            │
│                  │                               │
│  --- OR ---      │  [Download] [Edit]            │
│                  │                               │
│  Restaurant Name │  Edit Section:                │
│  Style Selector  │  [Edit instructions]          │
│  Add Items       │  [Apply Edit]                 │
│  Items List      │                               │
│                  │                               │
│  [Generate Menu] │                               │
└──────────────────┴──────────────────────────────┘
```

## 🔑 API Endpoints

### POST /api/surprise
Generates menu content from simple prompt
```json
{
  "prompt": "burger joint"
}
```

### POST /api/generate
Generates menu image from items
```json
{
  "restaurantName": "The Burger Joint",
  "items": [...],
  "style": "modern"
}
```

### POST /api/edit
Edits existing menu
```json
{
  "imageUrl": "https://...",
  "editInstruction": "Make text larger"
}
```

## 🧪 Test the "Surprise Me" Feature

1. Open http://localhost:3000
2. Type: "I want to start a pizza place"
3. Click "Generate Everything"
4. See: Restaurant name + full menu populated
5. Click "Generate Menu Image"
6. View your menu!
7. Edit if needed
8. Download!

## ✨ Surprise Me Templates

Currently supports:
- **Burger joints**: Generates burger menu
- **Pizza places**: Generates pizza menu
- **Coffee/Cafes**: Generates coffee shop menu
- **Generic**: Fallback template

(These are simple templates - you can enhance with real LLM later)
