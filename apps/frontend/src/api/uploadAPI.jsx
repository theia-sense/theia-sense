import axios from "axios";

const uploadClient = axios.create({
    baseURL: "http://localhost:8000",
    //timeout: 15000,
    headers: {
        "Content-Type": "multipart/form-data"
    }
});

export const uploadImagesToServer = async (formData) => {
    const response = await uploadClient.post("/predict/", formData);
    return response.data;
};

export default uploadClient;
