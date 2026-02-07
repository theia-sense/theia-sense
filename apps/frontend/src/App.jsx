
import DropFiles from "./components/DropFiles"
import ImageGallery from "./components/ImageGallery"
import Sidebar from './components/Sidebar';
import TagFilter from './components/TagFilter';
import useUploadImages from './hooks/useUploadImages'
import Hero from './components/Hero';
import Footer from './components/Footer'
import { FiPlus } from 'react-icons/fi'
import styles from './App.module.css'
import { useEffect, useRef } from "react";

function App() {

    const {
        state: { imagesToUpload, curatedImages, filteredImages, isUploading, selectedTags },
        actions: { addFiles, removeFile, uploadImages, filterByTags },
    } = useUploadImages();

    const galleryRef = useRef(null);
    useEffect(() => {
        if (curatedImages.length && galleryRef.current) {
            galleryRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [curatedImages]);
    return (
        <div className={styles.appContainer}>
            <div className={styles.appIntro}>
                <header className={styles.appHeader}>
                    <h1>THEIA SENSE</h1>
                    <div className={styles.navbar_divider}>
                        <span className={styles.plus_signs}><FiPlus /></span>
                        <div className={styles.divider_line}></div>
                        <span className={styles.plus_signs}><FiPlus /></span>
                    </div>
                </header>
                <Hero />
                <div className={styles.navbar_divider}>
                    <span className={styles.plus_signs}><FiPlus /></span>
                    <div className={styles.divider_line}></div>
                    <span className={styles.plus_signs}><FiPlus /></span>
                </div>
            </div>

            <div id="appLayout" className={styles.appLayout}>       

                <Sidebar images={imagesToUpload} onFilesRemoved={removeFile} isUploading={isUploading} />
                <main className={styles.mainContent}>
                    <DropFiles onFilesAdded={addFiles} />
                    <button
                        onClick={uploadImages}
                        disabled={isUploading || imagesToUpload.length === 0}
                        className="btn btn-primary"
                    >
                        {isUploading ? "Finding your best shots..." : `Upload ${imagesToUpload.length} Image(s)`}
                    </button>
                    
                    {curatedImages.length > 0 && (
                        <>
                            <TagFilter
                                images={curatedImages}
                                onTagFilter={filterByTags}
                                selectedTags={selectedTags}
                            />
                            <ImageGallery ref={galleryRef} images={filteredImages} />
                        </>
                    )}
                </main>
                
            </div>
            <div className={styles.appFooter}>
                <div className={styles.navbar_divider}>
                    <span className={styles.plus_signs}><FiPlus /></span>
                    <div className={styles.divider_line}></div>
                    <span className={styles.plus_signs}><FiPlus /></span>
                </div>
                <Footer />
            </div>

        </div>
    );
}

export default App
