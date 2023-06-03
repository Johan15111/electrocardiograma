import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from biosppy.signals import ecg
from collections import deque
import time

def init():
    ax.set_ylim(-100, 170)
    ax.set_title("Electrocardiograma en vivo")
    ax.set_ylabel("Milivoltios")
    ax.grid(True)
    return ln,

def init2():
    ax2.set_ylim(0, 200)  # Establece el rango de bpm según tus necesidades
    ax2.set_title("BPM en vivo")
    ax2.set_ylabel("BPM")
    ax2.grid(True)
    return ln2,

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
                    bpmdata.append(bpm)

            last_bpm_calculation = current_time

    except UnicodeDecodeError:
        print("Error al decodificar datos. Ignorando dato actual.")

    ln.set_data(range(len(ydata)), ydata)
    return ln,

def update2(frame):
    ax2.set_xlim(0, len(bpmdata))
    ln2.set_data(range(len(bpmdata)), bpmdata)
    return ln2,


if "__main__" == __name__:
    last_bpm_calculation = time.time()

    try:
        arduino_port = "COM3"
        baud_rate = 115200
        ser = serial.Serial(arduino_port, baud_rate)

        fig, ax = plt.subplots()
        ydata = deque(maxlen=150)
        ln, = plt.plot([], [], 'r', label="Valor analógico")

        fig2, ax2 = plt.subplots()
        bpmdata = deque(maxlen=150)
        ln2, = plt.plot([], [], 'b', label="BPM")

        ani = FuncAnimation(fig, update, frames=range(0, 100000), init_func=init, blit=True, interval=0)
        ani2 = FuncAnimation(fig2, update2, frames=range(0, 100000), init_func=init2, blit=True, interval=0)

        plt.show()

    finally:
        print("Finalizando...")
        ser.close()
