# 🚦 TrafficVision AI  
### Dynamic AI Traffic Flow Optimizer & Emergency Grid

TrafficVision AI is an intelligent traffic management system that uses **computer vision and AI-based object detection** to optimize traffic signal timings based on real-time traffic density.

The system analyzes live traffic camera feeds, detects vehicles using a **YOLO object detection model**, and dynamically adjusts traffic signals to reduce congestion. It also enables an **AI-powered green corridor** feature to prioritize emergency vehicles such as ambulances and fire trucks.

---

# 🚀 Features

- Real-time **vehicle detection using YOLO**
- **Traffic density analysis per lane**
- **Dynamic signal timing adjustment**
- **Emergency vehicle detection**
- Automatic **AI-powered green corridor**
- Smart **traffic monitoring dashboard**
- Simulation-based **hackathon demo system**

---

# 🧠 How It Works

1. Traffic cameras capture live video from road intersections.
2. Video feed is processed by a **YOLO object detection model**.
3. The model detects vehicles such as:
   - Cars
   - Buses
   - Bikes
   - Trucks
   - Ambulances
   - Fire trucks
4. The system calculates **traffic density for each lane**.
5. A **traffic optimization engine** dynamically adjusts signal timings.
6. If an **emergency vehicle is detected**, a **green corridor** is automatically activated.

---

# ⚙️ Traffic Signal Logic

Signal timings are dynamically adjusted based on vehicle count.

| Vehicles in Lane | Green Signal Time |
|------------------|------------------|
| 0 – 5 vehicles   | 10 seconds |
| 6 – 15 vehicles  | 20 seconds |
| 16 – 30 vehicles | 30 seconds |
| 30+ vehicles     | 45 seconds |

This ensures that **heavily congested lanes receive longer green signals**.

---

# 🏗 System Architecture

The system consists of four major components:

1. **Traffic Monitoring Layer**  
   Cameras capture real-time traffic video.

2. **Computer Vision Module**  
   YOLO model detects vehicles and calculates traffic density.

3. **Traffic Optimization Engine**  
   AI-based logic determines optimal signal timing.

4. **Emergency Priority System**  
   Detects emergency vehicles and activates green corridor.

---

# 🛠 Technologies Used

- **Python**
- **YOLO Object Detection**
- **OpenCV**
- **Computer Vision Algorithms**
- **Streamlit Dashboard**
- **NumPy / Pandas**

---

# 🎥 Demo (Hackathon Prototype)

For the hackathon demonstration, the system uses a **simulation-based traffic video feed**.

Demo workflow:

1. Traffic video is loaded into the system
2. AI model detects vehicles in real time
3. Traffic density is calculated
4. Dynamic signal timing is displayed on dashboard
5. If an ambulance is detected, **green corridor is activated**

---

---

# 👨‍💻 Contributors

This project was developed as part of a hackathon prototype by the following team members:

- **Rahul [NSUT]** – Computer Vision Implementation    
- **Raman [NSUT]** – Dashboard / UI  
- **Tarun [NSUT]** – Traffic Optimization Logic  
- **Ayushi [ANDC]** – Research / Documentation
- **Sidharth [USAR]** – AI/ML Development & System Design

---

# 🙌 Acknowledgment

This project was developed as a prototype for an AI-based intelligent traffic management system aimed at improving traffic flow and enabling emergency vehicle priority in smart city environments.

# 🌍 Future Scope

- Integration with **real traffic cameras**
- **GPS-based emergency vehicle tracking**
- Smart city **traffic control integration**
- AI-based **predictive traffic optimization**

---

# 📚 References

YOLO Object Detection  
https://pjreddie.com/darknet/yolo/

Ultralytics YOLO Documentation  
https://docs.ultralytics.com

OpenCV Computer Vision Library  
https://opencv.org/

IEEE Intelligent Transportation Systems Research  
https://ieeexplore.ieee.org/

---

# 👨‍💻 Team

Hackathon Project – AI Traffic Optimization System
