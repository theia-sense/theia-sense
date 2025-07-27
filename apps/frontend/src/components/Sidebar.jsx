
import React, { useState, useEffect } from "react";
import styles from "./Sidebar.module.css";
import { FiX, FiImage, FiTrash2, FiFolder, FiUpload } from "react-icons/fi";

export default function Sidebar({ images, onFilesRemoved, isUploading }) {
    const [previewUrls, setPreviewUrls] = useState([]);

    useEffect(() => {
        const urls = images.map(({ file }) => ({
            name: file.name,
            url: URL.createObjectURL(file),
        }));

        setPreviewUrls(urls);

        // Clean on unmount
        return () => {
            urls.forEach(({ url }) => URL.revokeObjectURL(url));
        };
    }, [images]);

    if (!images?.length) {
        return (
            <aside className={styles.sidebar}>
                <div className={styles.emptyState}>    
                    <FiFolder className={styles.emptyIcon} />                    
                    <h3 className={styles.emptyTitle}>No Images Selected</h3>
                    <p className={styles.emptyDescription}>
                        Choose images to upload and they'll appear here for review.
                    </p>
                </div>
            </aside>
        );
    }


    return (
        <aside className={styles.sidebar}>
            <div className={styles.sidebarHeader}>
                <div className={styles.headerContent}>
                    <div className={styles.titleSection}>
                        <FiUpload className={styles.headerIcon} />
                        <h2 className={styles.sidebarTitle}>Upload Queue</h2>
                    </div>
                    
                        <span className={styles.imageCount}>
                            {images.length} image{images.length === 1 ? '' : 's'}
                        </span>
                    
                </div>
                
                <button
                    onClick={() => onFilesRemoved()}
                    disabled={images.length === 0 || isUploading}
                    className={styles.clearAllButton}
                    title="Remove all images"
                >
                    <FiTrash2 className={styles.clearIcon} />
                    <span>Clear All</span>
                </button>
            </div>

            {isUploading && (
                <div className={styles.uploadingIndicator}>
                    <div className={styles.loadingSpinner}></div>
                    <span className={styles.uploadingText}>Processing images...</span>
                </div>
            )}

            <div className={styles.imagesList}>
                
                {images.map(({ file, originalName }) => {
                    const preview = previewUrls.find((u) => u.name === file.name);
                    return (
                        preview && (
                            <div key={file.name} className={styles.imageItem}>
                                <div className={styles.imagePreview}>
                                    {/*<img */}
                                    {/*    src={preview.url} */}
                                    {/*    alt={originalName}*/}
                                    {/*    className={styles.previewImage}*/}
                                    {/*/>*/}
                                    <div className={styles.iconBackground}>
                                        <FiImage className={styles.iconImage} />
                                    </div>
                                    <div className={styles.imageOverlay}>
                                        <FiImage className={styles.overlayIcon} />
                                    </div>
                                </div>
                                
                                <div className={styles.imageDetails}>
                                    <div className={styles.imageName}>
                                        {originalName}
                                    </div>                            
                                    <span className={styles.fileType}>
                                        {file.type.split('/')[1].toUpperCase()}
                                    </span>                                   
                                </div>

                                <button
                                    className={styles.removeButton}
                                    onClick={() => onFilesRemoved(file.name)}
                                    disabled={isUploading}
                                    title={`Remove ${originalName}`}
                                >
                                    <FiX />
                                </button>
                            </div>
                        )
                    );
                })}
                </div>   
        </aside>
    );
}