# Intelligent Access Control & Environmental Monitoring System

## 📌 Overview
This project presents a fully integrated IoT system for **access control and real-time environmental monitoring**. Built on Raspberry Pi, the system demonstrates an end-to-end data pipeline — from user authentication and sensor data collection to secure communication, storage, and visualization.

## 🚀 Features
- 🔐 RFID-based access control system with real-time authorization (grant/deny access)
- 📊 Live monitoring of environmental conditions (temperature, humidity, pressure)
- 📟 OLED display for local system status and sensor data visualization
- 📡 Asynchronous communication using MQTT protocol
- 📈 Data storage and time-series analysis using InfluxDB
- 📉 Interactive dashboards and real-time charts in Grafana
- 🔔 Visual and audio feedback using RGB LEDs and buzzer
- 🔒 Secure communication with TLS 1.2 encryption

## 🏗️ Architecture
The system consists of multiple integrated components:

- **Raspberry Pi** – collects sensor data and handles RFID input  
- **MQTT Broker (Mosquitto)** – enables lightweight communication between components  
- **Node-RED** – processes logic, handles access decisions, and routes data  
- **InfluxDB** – stores time-series data (sensor readings & access logs)  
- **Grafana** – visualizes data through dashboards and charts  

## 🔄 Data Flow
1. User scans RFID card  
2. Raspberry Pi sends data via MQTT  
3. Node-RED processes request and validates access  
4. System responds (LED + buzzer feedback)  
5. Data is securely stored in InfluxDB  
6. Grafana displays real-time and historical data  

## 🛠️ Technologies Used
- Python (Raspberry Pi communication & MQTT client)
- Node-RED (visual programming & system logic)
- MQTT (publish-subscribe messaging protocol)
- InfluxDB (time-series database)
- Grafana (data visualization)
- TLS 1.2 (secure communication)
- HTML/CSS/JavaScript (dashboard customization)

## 🔒 Security
- Implemented **TLS 1.2 encryption** for MQTT communication  
- Configured **self-signed Certificate Authority (CA)**  
- Secured data transmission on port **8883**  
- Protected against **Man-in-the-Middle (MITM)** attacks  

## 📊 Example Data Visualizations
- Temperature, humidity, and pressure charts  
- Access log history (user ID, timestamp, status)  

## 🎯 Project Goal
The goal was to design a **scalable and secure IoT system** that integrates hardware, backend services, and data visualization tools into a unified solution.

## 🧠 Skills Demonstrated
- IoT system design and integration  
- Backend communication and data pipelines  
- Secure network communication (TLS)  
- Working with time-series databases  
- Data visualization and monitoring systems  

## 📷 Screenshots
<img width="805" height="409" alt="image" src="https://github.com/user-attachments/assets/e95ce08f-60f2-40bd-b137-fdefc91bd2d4" />
<img width="807" height="405" alt="image" src="https://github.com/user-attachments/assets/e35b63e5-e12d-4a46-a128-e1e8097b2b60" />
<img width="805" height="391" alt="image" src="https://github.com/user-attachments/assets/db57dee6-87da-4f3c-a139-d076af9dabed" />
