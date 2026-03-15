<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/YOLOv8-Object%20Detection-FF6B35?style=for-the-badge"/>
<img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge"/>

<br/><br/>

```
 ████████╗██████╗  █████╗ ███████╗███████╗ ██╗ ██████╗
     ██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██╔════╝
██║   ██████╔╝███████║█████╗  █████╗  ██║██║
██║   ██╔══██╗██╔══██║██╔══╝  ██╔══╝  ██║██║
     ██║   ██║  ██║██║  ██║██║     ██║     ██║╚██████╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝ ╚═════╝
    
        V I S I O N   A I  —  Traffic Intelligence System
```

### 🚦 Dynamic AI Traffic Flow Optimizer & Emergency Green Corridor

*Real-time computer vision meets adaptive traffic control — built for smarter cities and faster emergency response.*

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Solution Architecture](#-solution-architecture)
- [How It Works](#️-how-it-works)
- [Traffic Signal Logic](#-traffic-signal-logic)
- [Emergency Vehicle Detection](#-emergency-vehicle-detection)
- [Project Structure](#-project-structure)
- [Tech Stack](#️-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Running the Dashboard](#-running-the-dashboard)
- [Dashboard Features](#-dashboard-features)
- [Future Scope](#-future-scope)
- [Team](#-team)
- [References](#-references)

---

## 🌐 Overview

**TrafficVision AI** is an intelligent, real-time traffic management system that replaces outdated fixed-timer signals with **AI-driven adaptive control**. Using a YOLOv8 object detection model fed by live camera footage, the system continuously analyzes vehicle density across lanes and adjusts signal timings on the fly.

When an emergency vehicle — ambulance, fire truck, or police vehicle — is detected, the system instantly activates a **Green Corridor**, clearing a path for priority passage with zero manual intervention.

> Built as a hackathon prototype for smart city infrastructure.

---

## 🧠 The Problem

Traditional traffic signals operate on rigid pre-programmed timers. They have no awareness of actual road conditions — a lane with 40 cars gets the same green time as an empty one. This causes:

- 🚗 Unnecessary congestion at low-traffic intersections
- ⏱️ Long wait times during off-peak hours
- 🚑 Delayed emergency response due to signal priority gaps
- 🌍 Higher vehicle emissions from idle time

---

## 🏗 Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      TrafficVision AI                           │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Traffic    │    │   Computer   │    │    Traffic       │   │
│  │   Camera     │───▶│   Vision     │──▶│  Optimization    │   │
│  │   Feed       │    │  (YOLOv8)    │    │    Engine        │   │
│  └──────────────┘    └──────────────┘    └──────┬───────────┘   │
│                             │                   │               │
│                             ▼                   ▼               │
│                    ┌──────────────┐    ┌──────────────────┐     │
│                    │  Emergency   │    │   Signal Timer   │     │
│                    │  Detection   │    │   Controller     │     │
│                    └──────┬───────┘    └──────────────────┘     │
│                           │                                     │
│                           ▼                                     │
│                  ┌──────────────────┐                           │
│                  │  Green Corridor  │                           │
│                  │   Activation     │                           │
│                  └──────────────────┘                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Streamlit Live Dashboard                   │    │
│  └─────────────────────────────────────────────────────────┘    │ 
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ How It Works

```
  📷 Camera Feed
       │
       ▼
  🤖 YOLOv8 Detection  ──────────────────────────┐
       │                                          │
       ▼                                          ▼
  🚗 Vehicle Count                    🚑 Emergency Vehicle?
  per Lane                                       │
       │                               YES ──────▼
       ▼                                   🟢 GREEN CORRIDOR
  📊 Density Analysis                      Activated
       │
       ▼
  ⏱️ Dynamic Signal Timing
  (10s / 20s / 30s / 45s)
       │
       ▼
  📺 Dashboard Update
```

**Step by step:**

1. Traffic cameras capture live video from road intersections
2. Each frame is processed by the YOLOv8 model in real time
3. Vehicles (cars, buses, bikes, trucks) are detected and counted per lane
4. Traffic density is calculated and fed into the optimization engine
5. Signal timings are dynamically adjusted based on the density table
6. If an emergency vehicle is detected → **Green Corridor Mode** activates immediately
7. All data streams live to the Streamlit dashboard

---

## 🚦 Traffic Signal Logic

Signal green times adapt dynamically to real-time lane density:

| Vehicles in Lane | Green Signal Duration | Density Level |
|:-----------------:|:---------------------:|:-------------:|
| 0 – 5 | 10 seconds | 🟢 Low |
| 6 – 15 | 20 seconds | 🟡 Moderate |
| 16 – 30 | 30 seconds | 🟠 High |
| 30+ | 45 seconds | 🔴 Critical |

Lanes with heavier traffic receive proportionally longer green signals — reducing bottlenecks without human intervention.

---

## 🚑 Emergency Vehicle Detection

The AI model recognizes the following emergency vehicle classes:

| Vehicle Type | Action Triggered |
|:------------:|:----------------:|
| 🚑 Ambulance | Green Corridor Activated |
| 🚒 Fire Truck | Green Corridor Activated |
| 🚓 Police Vehicle | Green Corridor Activated |

**Green Corridor Behavior:**
- All signals on the emergency vehicle's projected route switch to green
- Cross-traffic signals are held at red
- Alert is displayed on the dashboard with vehicle type
- Normal adaptive timing resumes after the vehicle passes

---

## 📁 Project Structure

```
TrafficVision-AI/
│
├── dashboard/              # Streamlit dashboard UI
│   └── app.py
│
├── detection/              # YOLOv8 vehicle detection logic
│   └── detector.py
│
├── models/                 # Trained YOLO model weights
│   └── yolov8_traffic.pt
│
├── traffic_engine/         # Signal timing optimization logic
│   └── optimizer.py
│
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|:----------:|:-------:|:-------:|
| Python | 3.10+ | Core language |
| YOLOv8 (Ultralytics) | Latest | Real-time object detection |
| OpenCV | 4.x | Video capture & frame processing |
| Streamlit | Latest | Live interactive dashboard |
| NumPy | Latest | Numerical computation |
| Pandas | Latest | Data analysis & logging |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Webcam or video file for input (simulation mode available)

### Clone the Repository

```bash
git clone https://github.com/SiddharthRiot/TrafficVision-AI.git
cd TrafficVision-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify YOLO Model

Ensure the model weights are present in the `models/` directory. If missing, YOLOv8 will auto-download a base model on first run:

```bash
ls models/
```

---

## 🖥 Running the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

**Demo mode** (uses a pre-recorded traffic video):
```bash
streamlit run dashboard/app.py -- --demo
```

---

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| 🎥 Live Video Feed | Real-time camera stream with detection overlay |
| 🔲 Bounding Boxes | Vehicle detection visualization with class labels |
| 📈 Density Meter | Live traffic density level per lane |
| 🚦 Signal Status | Current green/red state for each lane |
| ⏱️ Timer Display | Dynamic countdown for current green signal |
| 🚨 Emergency Alert | Real-time alert when emergency vehicle detected |
| 📋 Vehicle Log | Running count of detected vehicles by type |

---

## 🌍 Future Scope

- [ ] **Lane-wise analysis** — per-lane density tracking at multi-lane intersections
- [ ] **GPS-based emergency routing** — pre-clear signals along the full route of an emergency vehicle
- [ ] **Multi-camera monitoring** — handle multiple intersections simultaneously
- [ ] **Predictive traffic modeling** — AI-based forecasting of congestion patterns
- [ ] **Smart city integration** — connect with city-wide traffic management systems
- [ ] **Edge AI deployment** — run inference on embedded hardware (NVIDIA Jetson, Raspberry Pi)
- [ ] **Traffic analytics dashboard** — historical data, heatmaps, and insights

---

## 👥 Team

| Name | Institution | Role |
|:----:|:-----------:|:----:|
| **Siddharth** | USAR | AI/ML Development & System Design |
| **Rahul** | NSUT | Computer Vision Implementation |
| **Tarun** | NSUT | Traffic Optimization Logic |
| **Raman** | NSUT | Dashboard & UI |
| **Ayushi** | ANDC | Research & Documentation |

---

## 📚 References

- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com)
- [OpenCV Computer Vision Library](https://opencv.org)
- [IEEE Intelligent Transportation Systems](https://ieeexplore.ieee.org)
- [NVIDIA Deep Learning Resources](https://developer.nvidia.com/deep-learning)
- [Streamlit Documentation](https://docs.streamlit.io)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).  
Developed for educational and hackathon purposes.

---

<div align="center">

Made with ❤️ by Team TrafficVision AI

*Smarter signals. Faster cities. Safer roads.*

</div>
