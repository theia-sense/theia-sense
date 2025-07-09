import './App.css'
import DropFiles from "./components/DropFiles"
import ImageGallery from "./components/ImageGallery"
import useUploadImages from './hooks/useUploadImages'

function App() {

    const {
        state: { imagesToUpload, curatedImages, isUploading }, 
        actions: { addFiles, uploadImages }
    } = useUploadImages();

    return (
        <div style={{ maxWidth: "1600px", margin: "0 auto", padding: "24px" }}>

            <h1>Image Culling App</h1>

            <DropFiles onFilesAdded={addFiles} />
            <button
                onClick={uploadImages}
                disabled={isUploading || imagesToUpload.length === 0}
                style={{ padding: "12px 24px", margin: "12px 0" }}>
                {isUploading ? "Uploading..." : `Upload ${imagesToUpload.length} Image(s)`}
            </button>

            <ImageGallery images={curatedImages} />

        </div>
    )
}

export default App
