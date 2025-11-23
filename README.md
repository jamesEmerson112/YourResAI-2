# Restaurant Menu Creator

Simple web app to create restaurant menus using AI image generation.

## Features

- ✨ **Surprise Me**: Enter a simple prompt like "burger joint" and generate everything automatically
- 📝 **Manual Mode**: Add items one by one with full control
- 🎨 **Style Selector**: Modern, Vintage, Elegant, or Casual
- ✏️ **Edit Generated Menus**: Refine menus after generation
- 📥 **Download**: Save your menu as an image

## Setup

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on http://localhost:5000

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

Frontend runs on http://localhost:3000

## Usage

1. **Surprise Me Mode**: Enter "I want to start a burger joint" → Click "Generate Everything"
2. **Manual Mode**: Add restaurant name, select style, add menu items
3. Click "Generate Menu Image"
4. Edit if needed
5. Download your menu!

## Tech Stack

- **Frontend**: React
- **Backend**: Flask (Python)
- **AI**: fal.ai alpha-image-232 models
  - text-to-image for generation
  - edit-image for refinements
