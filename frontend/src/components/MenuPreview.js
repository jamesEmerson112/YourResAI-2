import React, { useState } from 'react';
import './MenuPreview.css';

function MenuPreview({ generatedImage, loading, onEdit }) {
  const [editInstruction, setEditInstruction] = useState('');
  const [showEditInput, setShowEditInput] = useState(false);

  const handleEdit = () => {
    if (!editInstruction.trim()) {
      alert('Please enter edit instructions');
      return;
    }

    onEdit(editInstruction);
    setEditInstruction('');
    setShowEditInput(false);
  };

  if (loading) {
    return (
      <div className="menu-preview">
        <div className="loading">
          <div className="spinner"></div>
          <p>Generating your menu...</p>
        </div>
      </div>
    );
  }

  if (!generatedImage) {
    return (
      <div className="menu-preview">
        <div className="placeholder">
          <h2>📋 Preview</h2>
          <p>Your generated menu will appear here</p>
          <div className="preview-icon">🍽️</div>
        </div>
      </div>
    );
  }

  return (
    <div className="menu-preview">
      <h2>Generated Menu</h2>

      <div className="image-container">
        <a href={generatedImage.imageUrl} target="_blank" rel="noopener noreferrer">
          <img src={generatedImage.imageUrl} alt="Generated Menu" />
          <div className="click-hint">Click to view full size in new tab</div>
        </a>
      </div>

      {generatedImage.items && generatedImage.items.some(item => item.imageUrl) && (
        <div className="food-images-section">
          <h3>Food Images</h3>
          <div className="food-images-grid">
            {generatedImage.items.filter(item => item.imageUrl).map((item, index) => (
              <div key={index} className="food-image-item">
                <img src={item.imageUrl} alt={item.name} />
                <p className="food-image-name">{item.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {showEditInput && (
        <div className="edit-section">
          <input
            type="text"
            value={editInstruction}
            onChange={(e) => setEditInstruction(e.target.value)}
            placeholder="e.g., Make text larger, fix Bruschetta price to $8"
            className="edit-input"
          />
          <button onClick={handleEdit} className="apply-edit-btn">
            Apply Edit
          </button>
        </div>
      )}
    </div>
  );
}

export default MenuPreview;
