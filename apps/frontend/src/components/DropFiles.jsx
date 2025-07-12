import React, { useState, useRef } from "react";
import styles from "./DropFiles.module.css";
import { FiUploadCloud } from "react-icons/fi";

export default function DropFiles({ onFilesAdded }) {
    const [isDragging, setIsDragging] = useState(false);
    const dragCounter = useRef(0);

    const handleDragEnter = (e) => {
        e.preventDefault();
        dragCounter.current += 1;
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        dragCounter.current -= 1;
        if (dragCounter.current === 0) {
            setIsDragging(false);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        dragCounter.current = 0;

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
            className={`${styles.dropArea} ${isDragging ? styles.dragActive : ""}`}
            onDrop={handleDrop}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
        >
            <FiUploadCloud className={styles.icon} />
            <p className={styles.text}>
                Drag and drop image files here, or click below to browse your device.
            </p>


            <input
                id="fileInput"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.webp,.bmp,.gif"
                onChange={handleInputChange}
                className={styles.fileInput}
            />

            <label htmlFor="fileInput" className={styles.fileLabel}>
                Browse Files
            </label>
        </div>
    );
}
