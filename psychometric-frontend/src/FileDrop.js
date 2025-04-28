// src/FileDrop.js

import React from 'react';

function FileDrop({ name, onFileSelect }) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSelect(name, file);
    }
  };

  return (
    <div className="file-drop">
      <input
        type="file"
        name={name}
        onChange={handleChange}
        className="file-input"
        accept=".xlsx,.xls"
      />
    </div>
  );
}

export default FileDrop;
