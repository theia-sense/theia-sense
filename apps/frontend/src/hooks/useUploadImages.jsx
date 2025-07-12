import { useState, useCallback, useEffect } from "react";
import axios from "axios"
import Pica from "pica"
import { v4 as uuidv4 } from "uuid";

const pica = Pica()
export default function useUploadImages() {
    const [imagesToUpload, setImagesToUpload] = useState([]);
    const [curatedImages, setCuratedImages] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    const addFiles = useCallback((files) => {
        const wrappedFiles = Array.from(files).map((file) => {
            const ext = file.name.split(".").pop().toLowerCase();
            const uuidName = `${uuidv4()}.${ext}`;
            const renamedFile = new File([file], uuidName, { type: file.type });
            return { file: renamedFile, originalName: file.name };
        });
        setImagesToUpload((prev) => [...prev, ...wrappedFiles]);
    }, []);

    const removeFile = useCallback((fileName) => {
        if (!fileName) {
            setImagesToUpload([]);
        }
        else {
            setImagesToUpload((prev) => prev.filter(({ file }) => file.name !== fileName)
            );
        }
    }, []);

    const uploadImages = async () => {
        if (!imagesToUpload.length) return alert("No files selected.");

        setIsUploading(true);

        try {
            // Resize all images to 224x224 using Pica
            const resizedImages = await Promise.all(
                imagesToUpload.map(async ({file}) => {
                    const imgElement = await loadImageElement(file);
                    const resizedCanvas = await resizeWithPica(imgElement, 224, 224);
                    return await canvasToFile(resizedCanvas, file.name)
                })
            );

            // Upload resized images
            const formData = new FormData();
            resizedImages.forEach((file) => formData.append("files", file));

            const res = await axios.post("http://localhost:8000/predict/", formData);
            const result = res.data;

            // Match accepted filenames to images
            const acceptedImages = imagesToUpload.filter(({file}) => result.some((item)=> item.filename === file.name));

            const imagesWithURLs = acceptedImages.map(({file, originalName }) => {
                const meta = result.find((item) => item.filename === file.name);
                return {
                    uuidName: file.name,
                    originalName,
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
        actions: { addFiles, removeFile, uploadImages }
    };
}

// Convert file to Image element
const loadImageElement = (file) => {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const reader = new FileReader();

        reader.onload = () => {
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = reader.result;
        };

        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};

const resizeWithPica = (image, width, height) => {
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    return pica.resize(image, canvas);
};

// Convert canvas to File (Blob + filename)
const canvasToFile = (canvas, filename) => {
    return new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
            if (!blob) return reject(new Error("Canvas toBlob failed"));
            const file = new File([blob], filename, { type: "image/png" });
            resolve(file);
        }, "image/png", 1.0);
    });
};