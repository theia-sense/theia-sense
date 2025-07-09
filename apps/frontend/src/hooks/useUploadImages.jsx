import { useState, useCallback, useEffect } from "react";
import axios from "axios"

export default function useUploadImages() {
    const [imagesToUpload, setFilesToUpload] = useState([]);
    const [curatedImages, setCuratedImages] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    const addFiles = useCallback((files) => {
        setFilesToUpload((prev) => [...prev, ...files]);
    }, []);

    const uploadImages = async () => {
        if (!imagesToUpload.length) return alert("No files selected.");

        const formData = new FormData();
        imagesToUpload.forEach((file) => formData.append("files", file));

        try {
            setIsUploading(true);
            const res = await axios.post("http://localhost:8000/predict/", formData);
            const result = res.data;

            // Match accepted filenames to images
            const acceptedImages = imagesToUpload.filter((file) => result.some((item)=> item.filename === file.name));

            const imagesWithURLs = acceptedImages.map((file) => {
                const meta = result.find((item) => item.filename === file.name);
                return {
                    name: file.name,
                    url: URL.createObjectURL(file),
                    tags: meta.tags,
                    score: meta.score,
                };
            });

            setCuratedImages(imagesWithURLs);
            // setFilesToUpload([]); // Optional, clear files after upload
        }
        catch (error) {
            console.error("Upload failed:", error);
            alert("Upload failed.")
        }
        finally {
            setIsUploading(false);
        }
    };

    // Cleanup blob URLs on unmount or change
    useEffect(() => {
        return () => {
            curatedImages.forEach((img) => URL.revokeObjectURL(img.url))
        };
    }, [curatedImages]);

    return {
        state: { imagesToUpload, curatedImages, isUploading },
        actions: { addFiles, uploadImages }
    };

}