
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

**FastAPI · React · ONNX Runtime · Docker · Azure · Hugging Face Spaces**

- Architected & deployed a full-stack microservices-based platform with a decoupled FastAPI backend and ML inference service, enabling scalable, low-latency processing (**<100ms API response**)  
- Built an AI-driven aesthetic scoring and personalization engine using embedding-based similarity and ranking algorithms  
- Optimized ML inference using **ONNX Runtime**, achieving **~75% reduction in container size** and improved throughput  
- Designed asynchronous pipelines for high-throughput image processing using Python and Pillow  
- Deployed distributed services on **Azure Container Apps** and **Hugging Face Spaces**, enabling independent scaling  
- Implemented dynamic ranking algorithms adapting to dataset distribution  

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
