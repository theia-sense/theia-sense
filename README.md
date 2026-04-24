
# Theia Sense - Personalized Image Curation Platform

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![ONNX](https://img.shields.io/badge/ONNX-Optimized-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

🔗 [**Live Demo**](https://theia.rutansh.dev)  
🔗 [**Repository**](https://github.com/theia-sense/theia-sense)  

---

## Overview

**Theia Sense** is a full-stack, cloud-native, microservices-based application that leverages machine learning to **analyze, rank, and personalize image collections** based on aesthetic quality and contextual relevance.

Designed with scalability and performance in mind, the system integrates **AI-driven ranking, optimized inference pipelines, and distributed cloud deployment**, enabling real-time curation for user-uploaded images.

---

## Real-World Use Cases

- Social Media Curation - Automatically select the best photos for platforms like Instagram or Google Photos
- Photographer Workflows - Reduce manual culling time by ranking large photo batches
- E-commerce Optimization - Surface the most relevant product images dynamically
- Recommendation Systems - Personalize visual content based on user preferences
  
---

## Demo

<p align="center">
  <img src="assets/demo.gif" alt="Theia Sense Demo" width="800"/>
</p>

---

## TLDR

**Personalized Image Curation Platform (Theia Sense)**  
*Machine Learning · Full-Stack · Cloud Systems*  

**FastAPI · React · Docker · Azure Container Apps · ONNX Runtime · Hugging Face Spaces**

- Architected & deployed a full-stack, microservices-based application using FastAPI, React, Docker, and Azure Container Apps, enabling image uploads and personalization with **<100ms API latency** and **100+ concurrent users** via asynchronous APIs  
- Built an AI-driven personalization and image aesthetic ranking engine using CLIP-based feature embeddings and similarity search, improving content relevance and achieving **25% increase in engagement (CTR/time spent)**  
- Optimized ML inference using **ONNX Runtime**, quantization, and batching, achieving **75% reduction in container size** and **2× throughput improvement**, reducing latency from **~80ms → ~35ms**  
- Developed asynchronous data pipelines using asyncio and Pillow, efficiently processing **50+ images per batch**, deployed across **Azure Container Apps** and **Hugging Face Spaces** with scalable, fault-tolerant services


---

## Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/theia-sense/theia-sense.git
cd theia-sense
```

### 2. Setup Environment
```bash
cp .env.example .env
```

### 3. Run with Docker
```bash
docker compose up --build
```

### 4. Access
- Backend API:
```bash
  http://localhost:8000
```
- Frontend:
```bash
  http://localhost:<port>
```


---

## System Architecture

```text
Frontend (React UI)
        │
        ▼
FastAPI Backend (Async API Layer)
        │
        ├───────────────┐
        ▼               ▼
ML Inference       Image Processing
(ONNX Runtime)     (Async + Pillow)

        ▼
Cloud Deployment
(Azure + Hugging Face Spaces)
```


---

## Key Features

### AI-Powered Image Ranking
- Embedding-based similarity scoring
- Aesthetic ranking engine
- Dynamic normalization

### High-Performance Inference
- ONNX Runtime optimization
- Reduced latency and model size
- Batch inference support

### Microservices Architecture
- Decoupled backend + ML services
- Independent scaling and fault isolation

### Cloud-Native Deployment
- Dockerized services
- Azure Container Apps
- Hugging Face Spaces

### Asynchronous Data Pipelines
- Concurrent image processing
- Efficient I/O with asyncio


---


## Tech Stack

**Backend & ML**
- Python, FastAPI, ONNX Runtime, NumPy, Pillow

**Frontend**
- React

**Infrastructure**
- Docker, Azure Container Apps, Hugging Face Spaces

---

## Project Structure

```
theia-sense/
│── apps/                 # Backend and services
│── tests/                # Test cases
│── compose.yml           # Docker orchestration
│── .env.example          # Environment variables
│── .github/workflows     # CI/CD pipelines
```

---

## Authors

### Aditya Patel  
[![Portfolio](https://img.shields.io/badge/Portfolio-Website-000?logo=google-chrome&logoColor=white)](https://adityapatl149.github.io)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adityapatel149)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github&logoColor=white)](https://www.github.com/adityapatel149)

### Rutansh Suthar  
[![Portfolio](https://img.shields.io/badge/Portfolio-Website-000?logo=google-chrome&logoColor=white)](https://rutansh.dev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rutansh-suthar/)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github&logoColor=white)](https://github.com/RutanshS)
