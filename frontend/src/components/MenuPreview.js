import React, { useState } from 'react';
import './MenuPreview.css';

function MenuPreview({ generatedImage, loading, onEdit, variants, activeVariant, onVariantSwitch }) {
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

  // Check if we're in variant mode
  const hasVariants = variants && variants[1] && variants[1].status !== 'idle';
  const currentVariant = hasVariants ? variants[activeVariant] : null;

  // Determine what to display
  const displayImage = currentVariant?.imageUrl || generatedImage?.imageUrl;
  const displayItems = currentVariant?.items || generatedImage?.items;
  const displayName = currentVariant?.restaurantName;

  if (loading && !hasVariants) {
    return (
      <div className="menu-preview">
        <div className="loading">
          <div className="spinner"></div>
          <p>Generating your menu...</p>
        </div>
      </div>
    );
  }

  if (!displayImage && !hasVariants) {
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
      {/* Variant Selector */}
      {hasVariants && (
        <div className="variant-selector">
          {[1, 2, 3].map((variantId) => {
            const variant = variants[variantId];
            const isActive = activeVariant === variantId;
            const isReady = variant?.status === 'ready';
            const isGenerating = variant?.status === 'generating';
            const isError = variant?.status === 'error';

            return (
              <button
                key={variantId}
                className={`variant-btn ${isActive ? 'active' : ''} ${!isReady ? 'disabled' : ''}`}
                onClick={() => isReady && onVariantSwitch(variantId)}
                disabled={!isReady}
              >
                <span className="variant-number">Variant {variantId}</span>
                {isGenerating && <span className="variant-status">⏳ Generating...</span>}
                {isReady && variant.restaurantName && (
                  <span className="variant-name">{variant.restaurantName}</span>
                )}
                {isError && <span className="variant-status error">❌ Error</span>}
              </button>
            );
          })}
        </div>
      )}

      {/* Display current variant or single menu */}
      {currentVariant?.status === 'generating' ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Generating variant {activeVariant}...</p>
        </div>
      ) : displayImage ? (
        <>
          <h2>{displayName || 'Generated Menu'}</h2>

          <div className="image-container">
            <a href={displayImage} target="_blank" rel="noopener noreferrer">
              <img src={displayImage} alt="Generated Menu" />
              <div className="click-hint">Click to view full size in new tab</div>
            </a>
          </div>

          {displayItems && displayItems.some(item => item.imageUrl) && (
            <div className="food-images-section">
              <h3>Food Images</h3>
              <div className="food-images-grid">
                {displayItems.filter(item => item.imageUrl).map((item, index) => (
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
        </>
      ) : (
        <div className="placeholder">
          <h2>📋 Preview</h2>
          <p>Your generated menu will appear here</p>
          <div className="preview-icon">🍽️</div>
        </div>
      )}
    </div>
  );
}

export default MenuPreview;
