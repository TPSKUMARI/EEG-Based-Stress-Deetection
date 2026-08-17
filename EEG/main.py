import os
import warnings
import time
import threading
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from pythonosc import dispatcher as osc_dispatcher
from pythonosc import osc_server
from EEG_generate_training_matrix import gen_training_matrix
import tkinter as tk
import socket

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Global variables
ip = "0.0.0.0"
port = 12345
filePath = 'EEG_Recordings.csv'
directory_path = 'C:\\Users\\SAMANTHIKA\\Desktop\\EEG_Demo3\\EEG\\'
output_file = 'out.csv'
model_path = 'best_weights.h5'
eeg_values = []
timestamp_base = time.time()


# Function to load the trained model
def load_model(path):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(2548,)),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    model.load_weights(path)
    model.compile(optimizer=tf.compat.v1.train.AdamOptimizer(),
                  loss=tf.compat.v1.losses.sparse_softmax_cross_entropy,
                  metrics=['accuracy'])
    return model


# Function to preprocess the EEG data
def preprocess_data(features):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    n_features_after_scaling = scaled_features.shape[1]

    if n_features_after_scaling < 2548:
        padding = np.zeros((scaled_features.shape[0], 2548 - n_features_after_scaling))
        scaled_features = np.concatenate((scaled_features, padding), axis=1)
    elif n_features_after_scaling > 2548:
        scaled_features = scaled_features[:, :2548]

    return scaled_features


def writeFileHeader():
    # Write CSV file header
    fileString = 'timestamps,TP9,AF7,AF8,TP10,Right AUX\n'
    with open(filePath, 'w') as file:
        file.write(fileString)


def eeg_handler(address: str, *args):
    global timestamp_base
    timestampStr = "{:.3f}".format(timestamp_base)
    timestamp_base += 0.04
    fileString = timestampStr

    if len(args) == 1:  # Only one value received
        for _ in range(5):  # Repeat the value for all columns
            formatted_arg = "{:.3f}".format(args[0])
            fileString += "," + formatted_arg
    else:
        for arg in args[:5]:
            formatted_arg = "{:.3f}".format(arg)
            fileString += "," + formatted_arg

    fileString += "\n"

    with open(filePath, 'a') as file:
        file.write(fileString)


def stream_eeg():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    sock.bind((ip, port))

    while True:
        # Receive data from the client
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes

        # Decode the received data
        received_data = data.decode("utf-8")

        # Call eeg_handler with the received data
        eeg_handler("", *map(float, received_data.split(',')))
        time.sleep(1)


def display_eeg():
    global eeg_values
    while True:
        print("EEG values:", eeg_values)
        time.sleep(1)


def real_time_prediction():
    batch_size = 80
    while True:
        eeg_data = pd.read_csv(directory_path + 'EEG_Recordings.csv')
        length = eeg_data.shape[0]
        for i in range(0, length, batch_size):
            if length - i >= batch_size:
                print(f"Processing data points {i + 1} to {i + batch_size}...")
                gen_training_matrix(directory_path=directory_path, output_file=output_file, cols_to_ignore=-1)
                features = pd.read_csv('out.csv').values
                processed_features = preprocess_data(features)
                model = load_model(model_path)
                predictions = model.predict(processed_features)
                # Calculate percentages for each label
                percentages = (predictions * 100).round(2)
                print("Prediction Percentages:")
                for percent in percentages:
                    print(f"STRESSED: {percent[0]}%, CALM: {percent[1]}%, GOOD MOOD: {percent[2]}%")
                # Update GUI in the main thread
                root.after(0, update_gui, percentages)
            else:
                print("EEG values:Waiting for 80 values to get the Results")
        eeg_values.clear()  # Clear EEG values after processing all batches
        time.sleep(1)

def update_gui(percentages):
    # Update label text in GUI
    stressed_label.config(text=f"STRESSED: {percentages[0][0]}%")
    calm_label.config(text=f"CALM: {percentages[0][1]}%")
    good_mood_label.config(text=f"GOOD MOOD: {percentages[0][2]}%")
    # Highlight stressed label if percentage is above 80
    stressed_label.config(fg="red" if percentages[0][0] > 80 else "black")

if __name__ == "__main__":
    # Start threads
    writeFileHeader()
    print("Listening on UDP port " + str(port))
    stream_thread = threading.Thread(target=stream_eeg)
    display_thread = threading.Thread(target=display_eeg)
    prediction_thread = threading.Thread(target=real_time_prediction)

    stream_thread.start()
    display_thread.start()
    prediction_thread.start()

    # Create GUI
    root = tk.Tk()
    # GUI creation code omitted for brevity
    root.title("EEG Mood Prediction")
    root.geometry("400x300")  # Fixed size for the GUI

    # Add some styling to the GUI
    root.configure(bg="#f0f0f0")
    label_font = ("Arial", 14)
    result_font = ("Arial", 12)

    # Title
    title_label = tk.Label(root, text="EEG Based Stress Detection", font=("Arial", 16), bg="#f0f0f0")
    title_label.pack(side="top", pady=10)

    # Button to stream data
    stream_button = tk.Button(root, text="Stream", font=label_font)
    stream_button.pack(pady=5)

    # Labels to display prediction percentages
    stressed_label = tk.Label(root, text="STRESSED: 0.00%", font=result_font, bg="#f0f0f0")
    stressed_label.pack(pady=5)
    calm_label = tk.Label(root, text="CALM: 0.00%", font=result_font, bg="#f0f0f0")
    calm_label.pack(pady=5)
    good_mood_label = tk.Label(root, text="GOOD MOOD: 0.00%", font=result_font, bg="#f0f0f0")
    good_mood_label.pack(pady=5)

    # Note
    note_label = tk.Label(root, text="If stress level goes higher than 80%, It will indicate in RED colour",
                          bg="#f0f0f0")
    note_label.pack(pady=5)

    root.mainloop()

