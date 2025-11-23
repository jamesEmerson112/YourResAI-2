import React, { useState } from 'react';
import './App.css';
import MenuForm from './components/MenuForm';
import MenuPreview from './components/MenuPreview';

function App() {
  const [restaurantName, setRestaurantName] = useState('');
  const [items, setItems] = useState([]);
  const [style, setStyle] = useState('modern');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [surprisePrompt, setSurprisePrompt] = useState('');

  const handleSurpriseMe = async () => {
    if (!surprisePrompt.trim()) {
      alert('Please enter a description (e.g., "burger joint")');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/surprise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: surprisePrompt }),
      });

      const data = await response.json();
      setRestaurantName(data.restaurantName);
      setItems(data.items);
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate menu');
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!restaurantName || items.length === 0) {
      alert('Please add restaurant name and menu items');
      return;
    }

    setLoading(true);
    setGeneratedImage(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          restaurantName,
          items,
          style,
        }),
      });

      const data = await response.json();
      setGeneratedImage(data);
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate menu image');
      setLoading(false);
    }
  };

  const handleEdit = async (editInstruction) => {
    if (!generatedImage) return;

    setLoading(true);

    try {
      const response = await fetch('/api/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imageUrl: generatedImage.imageUrl,
          editInstruction,
        }),
      });

      const data = await response.json();
      setGeneratedImage({ ...generatedImage, imageUrl: data.imageUrl });
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to edit menu');
      setLoading(false);
    }
  };

  const addItem = (item) => {
    setItems([...items, item]);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🍽️ Restaurant Menu Creator</h1>
      </header>

      <div className="container">
        <div className="left-panel">
          {/* Surprise Me Section */}
          <div className="surprise-section">
            <h2>✨ Surprise Me</h2>
            <input
              type="text"
              placeholder="e.g., I want to start a burger joint"
              value={surprisePrompt}
              onChange={(e) => setSurprisePrompt(e.target.value)}
              className="surprise-input"
            />
            <button onClick={handleSurpriseMe} disabled={loading} className="surprise-btn">
              Generate Everything
            </button>
          </div>

          <div className="divider">OR</div>

          {/* Manual Entry */}
          <MenuForm
            restaurantName={restaurantName}
            setRestaurantName={setRestaurantName}
            items={items}
            addItem={addItem}
            removeItem={removeItem}
            style={style}
            setStyle={setStyle}
          />

          <button
            onClick={handleGenerate}
            disabled={loading || !restaurantName || items.length === 0}
            className="generate-btn"
          >
            {loading ? 'Generating...' : 'Generate Menu Image'}
          </button>
        </div>

        <div className="right-panel">
          <MenuPreview
            generatedImage={generatedImage}
            loading={loading}
            onEdit={handleEdit}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
