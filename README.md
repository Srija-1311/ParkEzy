# 🚗 ParkEzy – Smart Parking Occupancy Detection System

ParkEzy is a computer vision-based parking occupancy detection system built using YOLOv8 and spatial geometry analysis.

It detects vehicles in parking lot images and determines whether each parking slot is occupied or vacant.

---

## 📌 Features

- Vehicle detection using YOLOv8
- Parking slot extraction from XML annotations
- Slot occupancy prediction using polygon containment
- Accuracy evaluation
- Modular and clean architecture

---

## 📂 Project Structure

ParkEzy/
│
├── data/
│ └── UFPR04/
│ ├── images/
│ └── xml/
│
├── separation.py
├── parse_slots.py
├── detect_cars.py
├── occupancy.py
├── evaluate.py
├── main.py
├── requirements.txt


---

## ⚙️ Installation

Clone the repository:

git clone https://github.com/Srija-1311/ParkEzy.git
cd ParkEzy


Install dependencies:

pip install -r requirements.txt

Download the PKLot UFPR04 dataset.

Place it in:

data/UFPR04/

Run the full evaluation pipeline:

python main.py


This will:

- Load images
- Detect cars
- Predict occupancy
- Compute final accuracy

---

## 📊 Output

The final accuracy will be printed in the terminal.

---

## 🧠 Model Used

YOLOv8 (Ultralytics)

