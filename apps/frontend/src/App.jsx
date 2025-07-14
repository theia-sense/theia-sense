import './App.css'
import DropFiles from "./components/DropFiles"
import ImageGallery from "./components/ImageGallery"
import Sidebar from './components/Sidebar';
import useUploadImages from './hooks/useUploadImages'

function App() {

    const {
        state: { imagesToUpload, curatedImages, isUploading}, 
        actions: { addFiles, removeFile, uploadImages }
    } = useUploadImages();

    return (
        <div className="appContainer">
            <header className="appHeader">
                <h1>Theia Sense</h1>
            </header>

            <div className="appLayout">
                <Sidebar images={imagesToUpload} onFilesRemoved={removeFile} isUploading={isUploading} />
                <main className="mainContent">
                    <DropFiles onFilesAdded={addFiles} />
                    <button
                        onClick={uploadImages}
                        disabled={isUploading || imagesToUpload.length === 0}
                        className="uploadButton"
                    >
                        {isUploading ? "Finding your best shots..." : `Upload ${imagesToUpload.length} Image(s)`}
                    </button>

                    <ImageGallery images={curatedImages} />
                </main>
            </div>
        </div>
    );
}

export default App
