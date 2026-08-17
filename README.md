# EEG Mood Detection Project

This project is a simple EEG-based system that detects a person's mood or stress level using brain signal data. It collects EEG data, processes it, and uses a trained machine learning model to predict whether the user is stressed, calm, or in a good mood.

## Project idea

The system is designed to:

- receive EEG data from a sensor/device
- process the data into useful features
- send data over UDP for real-time streaming
- run a trained TensorFlow model
- display live prediction results in a GUI

## Main files

- `main.py` - main Python script that starts the UDP listener, does prediction, and shows the GUI
- `attention.py` - simple EEG attention/focus calculation example
- `EEG_generate_training_matrix.py` - prepares EEG data for training
- `attention_level.ino` - Arduino sketch related to attention/focus calculation
- `udp_data_send.py` - sends CSV EEG data using UDP
- `best_weights.h5` - trained model weights
- `requirements.txt` - Python dependencies

## Technologies used

- Python
- TensorFlow / Keras
- NumPy
- Pandas
- Scikit-learn
- Tkinter
- UDP socket communication
- Arduino-based EEG data collection

## How it works

1. EEG data is collected from the device or simulation source.
2. The data is processed and converted into feature vectors.
3. The model predicts mood/stress percentages.
4. Results are displayed in a GUI window.

## Setup

Open the project folder and install the dependencies:

```bash
pip install -r requirements.txt
```

Then run the main script:

```bash
python main.py
```

## Notes

- This project is for learning and experimentation.
- Hardware and data source setup may vary depending on the EEG device used.
- The model expects EEG data in a specific format and may need tuning for your setup.

## Folder structure

```text
EEG_Demo3/
├── EEG/
│   ├── main.py
│   ├── attention.py
│   ├── EEG_generate_training_matrix.py
│   ├── EEG_Recordings.csv
│   ├── best_weights.h5
│   ├── out.csv
│   └── requirements.txt
├── udp/
│   └── udp_data_send.py
├── attention_level.ino
└── README.md
```

## Summary

This project is a basic EEG-based real-time mood and stress detection system with a simple GUI and machine learning model. It is useful as a prototype or learning project for brain-signal analysis and real-time classification.
