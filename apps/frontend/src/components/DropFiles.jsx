import React from "react"

export default function DropFiles({ onFilesAdded }) {
    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFiles = e.dataTransfer?.files;
        if (droppedFiles?.length) {
            onFilesAdded(Array.from(droppedFiles));
        }
    };

    const handleInputChange = (e) => {
        const selectedFiles = e.target.files;
        if (selectedFiles?.length) {
            onFilesAdded(Array.from(selectedFiles));
        }
    };

    return (
        <div onDrop={handleDrop} onDragOver={(e) => e.preventDefault()} style={{ border: "2px dashed #ccc", padding: "24px", marginBottom: "24px", textAlign: "center", cursor:"pointer" }}>

            <p>Drag & drop images here, or click below</p>

            <input id="fileInput" type="file" multiple accept="image/*" onChange={handleInputChange} style={{ display: "none" }} />

            <label htmlFor="fileInput" style={{ color: "blue", cursor: "pointer" }}>
                Select Images
            </label>

        </div>
    );
}