import React, { useState, useRef } from "react";
import "./MenuForm.css";

const CATEGORIES = [
  "Appetizers",
  "Main Course",
  "Pasta",
  "Burgers",
  "Sides",
  "Desserts",
  "Drinks",
];
const STYLES = [
  { value: "modern", label: "Modern" },
  { value: "vintage", label: "Vintage" },
  { value: "elegant", label: "Elegant" },
  { value: "casual", label: "Casual" },
];

function MenuForm({
  restaurantName,
  setRestaurantName,
  items,
  addItem,
  removeItem,
  style,
  setStyle,
}) {
  const [newItem, setNewItem] = useState({
    category: "Appetizers",
    name: "",
    price: "",
    description: "",
    imageUrl: "",
  });

  const fileInputRef = useRef(null);

  const handleAddItem = () => {
    if (!newItem.name || !newItem.price) {
      alert("Please fill in item name and price");
      return;
    }

    addItem({
      ...newItem,
      price: parseFloat(newItem.price),
    });

    setNewItem({
      category: "Appetizers",
      name: "",
      price: "",
      description: "",
      imageUrl: "",
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleEdit = (index) => {
    const itemToEdit = items[index];
    setNewItem(itemToEdit);
    removeItem(index);
  };

  const handleImageFile = (file) => {
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setNewItem({ ...newItem, imageUrl: event.target.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePaste = (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        handleImageFile(file);
        break;
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleImageFile(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
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
          onChange={(e) =>
            setNewItem({ ...newItem, description: e.target.value })
          }
          placeholder="Fresh mozzarella, tomatoes, basil"
        />
      </div>

      <div
        className="form-group"
        onPaste={handlePaste}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <label>Image (optional)</label>
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={(e) => handleImageFile(e.target.files[0])}
        />
        <p style={{ fontSize: "0.9rem", color: "#555" }}>
          Upload an image, or leave blank to use a realistic AI-generated image.
        </p>
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
                <span
                  className="item-category"
                  style={{ marginInlineEnd: "1.5ch" }}
                >
                  {item.category}
                </span>
                <strong>{item.name}</strong> - ${item.price}
                <br></br>
                {item.description && (
                  <div className="item-desc">{item.description}</div>
                )}
                {item.imageUrl && (
                  <img
                    src={item.imageUrl}
                    alt="Menu item"
                    style={{
                      maxHeight: "100px",
                      maxWidth: "300px",
                      marginTop: "0.5rem",
                    }}
                  />
                )}
                {!item.imageUrl && (
                  "(Will use an AI-generated image)"
                )}
              </div>
              <button onClick={() => handleEdit(index)} className="edit-btn">
                ✏️
              </button>
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
