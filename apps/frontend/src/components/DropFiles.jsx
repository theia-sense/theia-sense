
 import React, { useState, useRef } from "react";
 import styles from "./DropFiles.module.css";
 import { FiUploadCloud, FiImage, FiPlus, FiZap } from "react-icons/fi";

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
             "image/bmp"
         ];
         return files.filter(file => supportedTypes.includes(file.type));
     };

     return (
         <div
             className={`${styles.dropZone} ${isDragging ? styles.isDragging : ""}`}
             onDrop={handleDrop}
             onDragEnter={handleDragEnter}
             onDragLeave={handleDragLeave}
             onDragOver={handleDragOver}
         >
             <div className={styles.dropContent}>
                 <div className={styles.iconStack}>
                     <FiUploadCloud className={styles.mainIcon} />
                     <div className={styles.floatingElements}>
                         <FiImage className={`${styles.floatingIcon} ${styles.float1}`} />
                         <FiZap className={`${styles.floatingIcon} ${styles.float2}`} />
                         <FiPlus className={`${styles.floatingIcon} ${styles.float3}`} />
                     </div>
                 </div>
                
                 <div className={styles.textSection}>
                     <h3 className={styles.primaryText}>
                         {isDragging ? "Drop your images here!" : "Upload Your Images"}
                     </h3>
                     <p className={styles.secondaryText}>
                         Drag and drop your photos here, or click to browse
                     </p>
                     <div className={styles.supportInfo}>
                         <span className={styles.supportLabel}>Supported formats:</span>
                         <span className={styles.formatList}>JPG, PNG, WEBP, BMP</span>
                     </div>
                 </div>

                 <input
                     id="fileInput"
                     type="file"
                     multiple
                     accept=".jpg,.jpeg,.png,.webp,.bmp,.gif"
                     onChange={handleInputChange}
                     className={styles.hiddenInput}
                 />

                 <label htmlFor="fileInput" className={`btn btn-secondary ${styles.browseButton}`}>
                     <FiPlus className={styles.buttonIcon} />
                     Browse Files
                 </label>
             </div>
         </div>
     );
 }
