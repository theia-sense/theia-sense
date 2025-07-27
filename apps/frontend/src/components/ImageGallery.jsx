
import React, { useState, forwardRef } from "react";
import JSZip from "jszip";
import { FiDownload, FiImage, FiTag, FiEye, FiFile, FiX } from "react-icons/fi";
import styles from "./ImageGallery.module.css";

const ImageGallery = forwardRef(({ images }, ref) => {
    const [selectedImage, setSelectedImage] = useState(null);

    if (!images?.length) return null;

    const handleDownloadZip = async () => {
        const zip = new JSZip();
        const folder = zip.folder("best-images");

        await Promise.all(
            images.map(async ({ uuidName, originalName, url }) => {
                try {
                    const response = await fetch(url);
                    const blob = await response.blob();
                    const filename = originalName || `${uuidName}.jpg`;
                    folder.file(filename, blob);
                } catch (err) {
                    console.error(`Failed to download image: ${url}`, err);
                }
            })
        );

        const zipBlob = await zip.generateAsync({ type: "blob" });
        const zipUrl = URL.createObjectURL(zipBlob);

        const a = document.createElement("a");
        a.href = zipUrl;
        a.download = "best-images.zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        URL.revokeObjectURL(zipUrl);
    };

    const openImageModal = (image) => {
        setSelectedImage(image);
    };

    const closeImageModal = () => {
        setSelectedImage(null);
    };

    const getScoreColor = (score) => {
        if (score >= 6.0) return styles.scoreAmazing;
        if (score >= 5.0) return styles.scoreExcellent;
        if (score >= 4.0) return styles.scoreGood;
        if (score >= 3.0) return styles.scoreFair;
        return styles.scorePoor;
    };

    const getScoreLabel = (score) => {
        if (score >= 6.0) return "Amazing";
        if (score >= 5.0) return "Excellent";
        if (score >= 4.0) return "Good";
        if (score >= 3.0) return "Fair";
        return "Poor";
    };

    return (
        <>
            <div ref={ref} className={styles.galleryContainer}>
                <div className={styles.galleryHeader}>
                    <div className={styles.headerContent}>
                        <div className={styles.titleSection}>
                            {/*<FiStar className={styles.headerIcon} />*/}
                            <div className={ styles.starWrapper}>
                            <svg
                                className={styles.starIcon}
                                viewBox="0 0 24 24"
                                fill="url(#starGradient)"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <defs>
                                    <linearGradient id="starGradient" x1="0" y1="0" x2="1" y2="1">
                                        <stop offset="0%" stopColor="#667eea" />
                                        <stop offset="100%" stopColor="#764ba2" />
                                    </linearGradient>
                                </defs>

                                <path
                                    d="M12 2.5L14.79 8.26L21.25 9.27L16.5 13.97L17.66 20.43L12 17.27L6.34 20.43L7.5 13.97L2.75 9.27L9.21 8.26L12 2.5Z"
                                    stroke="none"
                                    strokeLinejoin="round"
                                    strokeLinecap="round"
                                />
                            </svg>

                            </div>
                            <h3 className={styles.galleryTitle}>Best Images</h3>
                            <span className={styles.imageCount}>
                                {images.length} image{images.length === 1 ? '' : 's'}
                            </span>
                        </div>

                        <button
                            className={`btn btn-primary ${styles.downloadButton}`}
                            onClick={handleDownloadZip}
                            title="Download all images as ZIP"
                        >
                            <FiDownload className={styles.downloadIcon} />
                            <span>Download All</span>
                        </button>
                    </div>
                </div>

                <div className={styles.imageGrid}>
                    {images.map(({ uuidName, originalName, thumbnailUrl, url, score, tags }) => (
                        <div
                            key={uuidName}
                            className={styles.imageCard}
                            onClick={() => openImageModal({ uuidName, originalName, url, score, tags })}
                        >
                            <div className={styles.imageContainer}>
                                <img
                                    src={thumbnailUrl}
                                    alt={originalName}
                                    className={styles.image}
                                    loading="lazy"
                                />
                                <div className={styles.imageOverlay}>
                                    <button className={styles.viewButton}>
                                        <FiEye />
                                        <span>View</span>
                                    </button>
                                </div>
                            </div>

                        </div>
                    ))}
                </div>
            </div>

            {/* Image Modal */}
            {selectedImage && (
                <div className={styles.modal} onClick={closeImageModal}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <div className={styles.modalTitle}>
                                <FiFile className={styles.modalIcon} />
                                {selectedImage.originalName}
                            </div>
                            <button
                                className={styles.closeButton}
                                onClick={closeImageModal}
                            >
                                <FiX />
                            </button>
                        </div>

                        <div className={styles.modalBody}>
                            <div className={styles.modalImageContainer}>
                                <img
                                    src={selectedImage.url}
                                    alt={selectedImage.originalName}
                                    className={styles.modalImage}
                                />
                            </div>

                            <div className={styles.modalInfo}>
                                <div className={styles.modalTagsSection}>
                                    <h4>Detected Tags</h4>
                                    <div className={styles.modalTagsList}>
                                        {selectedImage.tags.map((tag, index) => (
                                            <span key={index} className={styles.modalTag}>
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
});

export default ImageGallery;