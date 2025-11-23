import React, { useState, useEffect, useRef } from 'react';
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

  // New state for 3-variant system
  const [variants, setVariants] = useState({
    1: null,
    2: { status: 'idle' },
    3: { status: 'idle' }
  });
  const [activeVariant, setActiveVariant] = useState(1);
  const [sessionId, setSessionId] = useState(null);
  const pollingInterval = useRef(null);

  // Polling mechanism to check variant status
  useEffect(() => {
    if (sessionId) {
      // Start polling every 3 seconds
      pollingInterval.current = setInterval(async () => {
        try {
          const response = await fetch(`/api/check-variant-status/${sessionId}`);
          const data = await response.json();

          setVariants({
            1: data.variant1,
            2: data.variant2,
            3: data.variant3
          });

          // Stop polling if all variants are ready
          if (data.allReady) {
            clearInterval(pollingInterval.current);
            pollingInterval.current = null;
            console.log('✓ All variants ready!');
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 3000);

      // Cleanup on unmount
      return () => {
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
        }
      };
    }
  }, [sessionId]);

  const handleSurpriseMe = async () => {
    if (!surprisePrompt.trim()) {
      alert('Please enter a description (e.g., "burger joint")');
      return;
    }

    setLoading(true);
    setActiveVariant(1);
    setVariants({
      1: { status: 'generating' },
      2: { status: 'generating' },
      3: { status: 'generating' }
    });

    try {
      // Use new variant generation endpoint
      const response = await fetch('/api/generate-variants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: surprisePrompt }),
      });

      const data = await response.json();

      // Store session ID for polling
      setSessionId(data.sessionId);

      // Update variants state with initial data
      setVariants({
        1: data.variant1,
        2: data.variant2,
        3: data.variant3
      });

      // Set restaurant data from variant 1 for manual editing if needed
      if (data.variant1.status === 'ready') {
        setRestaurantName(data.variant1.restaurantName);
        setItems(data.variant1.items);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate menu variants');
      setLoading(false);
    }
  };

  const handleVariantSwitch = (variantId) => {
    setActiveVariant(variantId);
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
            variants={variants}
            activeVariant={activeVariant}
            onVariantSwitch={handleVariantSwitch}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
