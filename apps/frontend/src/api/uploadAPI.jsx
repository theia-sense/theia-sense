import axios from "axios";

const uploadClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "https://api.rutansh.dev",
    timeout: 300000,
    headers: {
        "Content-Type": "multipart/form-data"
    }
});

export const uploadImagesToServer = async (formData) => {
    const response = await uploadClient.post("/predict/", formData);
    return response.data;
};

export default uploadClient;
