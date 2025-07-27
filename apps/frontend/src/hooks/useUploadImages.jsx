import { useState, useCallback, useEffect, useMemo } from "react";
import { uploadImagesToServer } from "../api/uploadAPI";
import Pica from "pica"
import { v4 as uuidv4 } from "uuid";

const pica = Pica()

// Detect mobile and device memory
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isAndroid = /Android/.test(navigator.userAgent);
const isMobile = isIOS || isAndroid;
const deviceMemoryGB = navigator.deviceMemory || 4; //fallback to 4

const getBatchSize = () => {
    if (isMobile) {
        if (deviceMemoryGB <= 2) return 4;
        if (deviceMemoryGB <= 4) return 6;
        return 8;
    } else {
        if (deviceMemoryGB <= 4) return 8;
        if (deviceMemoryGB <= 8) return 16;
        return 32;
    }
};

export default function useUploadImages() {
    const [imagesToUpload, setImagesToUpload] = useState([]);
    const [curatedImages, setCuratedImages] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [selectedTags, setSelectedTags] = useState([]); // New state for tag filtering

    const filteredImages = useMemo(() => {
        if (!selectedTags.length) return curatedImages;
        
        return curatedImages.filter(image => 
            selectedTags.some(selectedTag => 
                image.tags?.includes(selectedTag)
            )
        );
    }, [curatedImages, selectedTags]);

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

        // Resize all images to 224x224 using Pica in batches to optimize memory usage
        try {
            const batchSize = getBatchSize();
            const resizedImages = [];
            const thumbnails = [];
            for (let i = 0; i < imagesToUpload.length; i += batchSize){
                const batch = imagesToUpload.slice(i, i + batchSize);

                const resizedBatch = await Promise.all(
                    batch.map(async ({ file }) => {
                        const imgBitmap = await loadImageBitmap(file);
                        // For backend api
                        const resizedCanvas = await resizeWithPica(imgBitmap, 224, 224);
                        const resizedFile = await canvasToFile(resizedCanvas, file.name);

                        // Thumbnail preserving aspect ratio
                        const thumbnailCanvas = await resizeWithAR(imgBitmap, 480);
                        const thumbnailFile = await canvasToFile(thumbnailCanvas, file.name, "webp");

                        if (imgBitmap.close) imgBitmap.close();

                        return { resizedFile, thumbnailFile };
                    })
                );

                resizedImages.push(...resizedBatch.map(item => item.resizedFile));
                thumbnails.push(...resizedBatch.map(item => item.thumbnailFile));
            }

            // Upload resized files
            const formData = new FormData();
            resizedImages.forEach((file) => formData.append("files", file));

           const result = await uploadImagesToServer(formData);

            // Match accepted filenames to images
            const acceptedImages = imagesToUpload.filter(({file}) => result.some((item)=> item.filename === file.name));

            const imagesWithURLs = acceptedImages.map(({file, originalName }) => {
                const meta = result.find((item) => item.filename === file.name);
                const thumb = thumbnails.find(t => t.name === file.name);
                return {
                    uuidName: file.name,
                    originalName,
                    url: URL.createObjectURL(file),
                    thumbnailUrl: URL.createObjectURL(thumb),
                    tags: meta.tags,
                    score: meta.score,
                };
            });

            setCuratedImages(imagesWithURLs);
            // setFilesToUpload([]); // Optional, clear files after upload
        }
        catch (error) {
            console.error("Upload failed:", error);
            alert(`Upload failed: ${error?.message || "Unknown error"}`);
        }
        finally {
            setIsUploading(false);
        }
    };

    const filterByTags = useCallback((tags) => {
        setSelectedTags(tags);
    }, []);

    const clearTagFilter = useCallback(() => {
        setSelectedTags([]);
    }, []);



    // Cleanup blob URLs on unmount or change
    useEffect(() => {
        return () => {
            curatedImages.forEach((img) => {
                if (img.url) URL.revokeObjectURL(img.url);
                if (img.thumbnailUrl) URL.revokeObjectURL(img.thumbnailUrl);
            });
        };
    }, [curatedImages]);

    // return {
    //     state: { imagesToUpload, curatedImages, isUploading },
    //     actions: { addFiles, removeFile, uploadImages }
    // };
    return {
        state: { 
            imagesToUpload, 
            curatedImages, 
            filteredImages,  // Add filtered images
            isUploading,
            selectedTags     // Add selected tags
        },
        actions: { 
            addFiles, 
            removeFile, 
            uploadImages,
            filterByTags,    // Add tag filtering
            clearTagFilter   // Add clear filter
        }
    };
}

// Convert file to Image bitmap or use ImageElement as fallback if ImageBitmap not supported
const loadImageBitmap = async (file) => {

    if ("createImageBitmap" in window) {
        try {
            return await createImageBitmap(file);
        }
        catch (error) {
            console.warn("createImageBitmap failed, falling back:", error);
        }
    }

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
const canvasToFile = (canvas, filename, format = "png") => {
    return new Promise((resolve, reject) => {
        const mimeType = format === "webp" ? "image/webp" : "image/png";
        canvas.toBlob((blob) => {
            if (!blob) return reject(new Error("Canvas toBlob failed"));
            const file = new File([blob], filename, { type: mimeType });
            resolve(file);
        }, mimeType, 1.0);
    });
};

const resizeWithAR = async (image, maxSize) => {
    // .width for imagebitmap or .naturalWidth for HTMLImageElement
    let origWidth = image.width || image.naturalWidth;
    let origHeight = image.height || image.naturalHeight;

    const scale = Math.min(maxSize / origWidth, maxSize / origHeight);
    const w = Math.round(origWidth * scale);
    const h = Math.round(origHeight * scale);

    return await resizeWithPica(image, w, h);
};