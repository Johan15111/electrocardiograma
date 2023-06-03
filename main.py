import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from biosppy.signals import ecg
from collections import deque
import time

def init():
    ax.set_ylim(-70, 170)
    ax.set_title("Electrocardiograma en vivo")
    ax.set_ylabel("Milivoltios")
    ax.grid(True)
    return ln,

def calculate_bpm(ecg_data, sampling_rate):
    out = ecg.hamilton_segmenter(ecg_data, sampling_rate=sampling_rate)
    rpeaks = out['rpeaks']

    if len(rpeaks) > 1:
        time_intervals = np.diff(rpeaks) / sampling_rate
        avg_time_interval = np.mean(time_intervals)
        bpm = 60 / avg_time_interval
    else:
        bpm = None

    return bpm

def update(frame):
    global last_bpm_calculation
    current_time = time.time()

    try:
        value = ser.readline().decode('utf-8', errors='ignore').strip()
        if value.isalpha() or value == '':
            ydata.append(0)
        else:
            ydata.append(float(value))

        ax.set_xlim(0, len(ydata))

        if current_time - last_bpm_calculation >= 3:
            if len(ydata) > 15:
                ydata_np = np.array(ydata)
                bpm = calculate_bpm(ydata_np, sampling_rate=66.67)
                if bpm is not None:
                    print(bpm)

            last_bpm_calculation = current_time

    except UnicodeDecodeError:
        print("Error al decodificar datos. Ignorando dato actual.")

    ln.set_data(range(len(ydata)), ydata)
    return ln,


if "__main__" == __name__:
    last_bpm_calculation = time.time()

    try:
        arduino_port = "COM3"
        baud_rate = 115200
        ser = serial.Serial(arduino_port, baud_rate)

        fig, ax = plt.subplots()
        ydata = deque(maxlen=150)
        ln, = plt.plot([], [], 'r', label="Valor analógico")

        ani = FuncAnimation(fig, update, frames=range(0, 100000), init_func=init, blit=True, interval=0)

        plt.show()

    finally:
        print("Finalizando...")
        ser.close()