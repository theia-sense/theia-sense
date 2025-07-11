import React from "react";

export default function DropFiles({ onFilesAdded }) {
    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFiles = e.dataTransfer?.files;
        if (droppedFiles?.length) {
            const filteredFiles = filterSupportedImages(Array.from(droppedFiles));
            onFilesAdded(filteredFiles);
        }
    };

    const handleInputChange = (e) => {
        const selectedFiles = e.target.files;
        if (selectedFiles?.length) {
            const filteredFiles = filterSupportedImages(Array.from(selectedFiles));
            onFilesAdded(filteredFiles);
        }
    };

    const filterSupportedImages = (files) => {
        const supportedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/bmp",
            "image/gif"
        ];
        return files.filter(file => supportedTypes.includes(file.type));
    };

    return (
        <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            style={{
                border: "2px dashed #ccc",
                padding: "24px",
                marginBottom: "24px",
                textAlign: "center",
                cursor: "pointer"
            }}
        >
            <p>Drag & drop supported images here, or click below</p>

            <input
                id="fileInput"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.webp,.bmp,.gif"
                onChange={handleInputChange}
                style={{ display: "none" }}
            />

            <label htmlFor="fileInput" style={{ color: "blue", cursor: "pointer" }}>
                Select Images
            </label>
        </div>
    );
}
