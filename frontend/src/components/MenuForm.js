import React, { useState } from 'react';
import './MenuForm.css';

const CATEGORIES = ['Appetizers', 'Main Course', 'Pasta', 'Burgers', 'Sides', 'Desserts', 'Drinks'];
const STYLES = [
  { value: 'modern', label: 'Modern' },
  { value: 'vintage', label: 'Vintage' },
  { value: 'elegant', label: 'Elegant' },
  { value: 'casual', label: 'Casual' },
];

function MenuForm({ restaurantName, setRestaurantName, items, addItem, removeItem, style, setStyle }) {
  const [newItem, setNewItem] = useState({
    category: 'Appetizers',
    name: '',
    price: '',
    description: '',
    imageUrl: '',
  });

  const handleAddItem = () => {
    if (!newItem.name || !newItem.price) {
      alert('Please fill in item name and price');
      return;
    }

    addItem({
      ...newItem,
      price: parseFloat(newItem.price),
    });

    setNewItem({
      category: 'Appetizers',
      name: '',
      price: '',
      description: '',
      imageUrl: '',
    });
  };

  return (
    <div className="menu-form">
      <div className="form-group">
        <label>Restaurant Name</label>
        <input
          type="text"
          value={restaurantName}
          onChange={(e) => setRestaurantName(e.target.value)}
          placeholder="Enter restaurant name"
        />
      </div>

      <div className="form-group">
        <label>Menu Style</label>
        <select value={style} onChange={(e) => setStyle(e.target.value)}>
          {STYLES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <hr />

      <h3>Add Menu Item</h3>

      <div className="form-group">
        <label>Category</label>
        <select
          value={newItem.category}
          onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
        >
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Item Name</label>
        <input
          type="text"
          value={newItem.name}
          onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
          placeholder="e.g., Margherita Pizza"
        />
      </div>

      <div className="form-group">
        <label>Price ($)</label>
        <input
          type="number"
          step="0.01"
          value={newItem.price}
          onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
          placeholder="12.99"
        />
      </div>

      <div className="form-group">
        <label>Description</label>
        <input
          type="text"
          value={newItem.description}
          onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
          placeholder="Fresh mozzarella, tomatoes, basil"
        />
      </div>

      <div className="form-group">
        <label>Image URL (optional)</label>
        <input
          type="text"
          value={newItem.imageUrl}
          onChange={(e) => setNewItem({ ...newItem, imageUrl: e.target.value })}
          placeholder="https://... or leave blank to auto-generate"
        />
        <small style={{color: '#666', fontSize: '0.85rem', marginTop: '0.25rem', display: 'block'}}>
          Paste an image URL or leave blank to auto-generate a realistic food image
        </small>
      </div>

      <button onClick={handleAddItem} className="add-item-btn">
        + Add Item
      </button>

      {items.length > 0 && (
        <div className="items-list">
          <h3>Menu Items ({items.length})</h3>
          {items.map((item, index) => (
            <div key={index} className="menu-item">
              <div className="item-info">
                <span className="item-category">{item.category}</span>
                <strong>{item.name}</strong> - ${item.price}
                {item.description && <div className="item-desc">{item.description}</div>}
                {item.imageUrl && <div className="item-image-indicator">📷 Image provided</div>}
                {!item.imageUrl && <div className="item-image-indicator" style={{color: '#999'}}>🎨 Will auto-generate</div>}
              </div>
              <button onClick={() => removeItem(index)} className="remove-btn">
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MenuForm;
