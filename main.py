import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from biosppy.signals import ecg
from collections import deque
import time

# Configuración para ocultar los botones y controles
plt.rcParams['toolbar'] = 'None'  # Oculta la barra de herramientas
plt.rcParams['keymap.fullscreen'] = []  # Desactiva el atajo de pantalla completa
plt.rcParams['keymap.home'] = []  # Desactiva el atajo de restablecer la vista
plt.rcParams['keymap.save'] = []  # Desactiva el atajo de guardar el gráfico
plt.rcParams['keymap.zoom'] = []  # Desactiva el atajo de hacer zoom

def init_electrocardiograma():
    ax_electrocardiograma.set_ylim(-100, 170)
    ax_electrocardiograma.set_title("Electrocardiograma en vivo")
    ax_electrocardiograma.set_ylabel("Milivoltios")
    ax_electrocardiograma.set_xticklabels([]) 
    ax_electrocardiograma.grid(True)
    return ln,

def init_grafica_bpm():
    ax_bpm_grafico.set_ylim(0, 200)
    ax_bpm_grafico.set_title("Latidos por minuto en vivo")
    ax_bpm_grafico.set_ylabel("BPM")
    ax_bpm_grafico.set_xticklabels([]) 
    ax_bpm_grafico.grid(True)
    return ln2,

def calcular_bpm(ecg_data, sampling_rate):
    out = ecg.hamilton_segmenter(ecg_data, sampling_rate=sampling_rate)
    rpeaks = out['rpeaks']

    if len(rpeaks) > 1:
        time_intervals = np.diff(rpeaks) / sampling_rate
        avg_time_interval = np.mean(time_intervals)
        bpm = 60 / avg_time_interval
    else:
        bpm = None

    return bpm

def update_electrocardiograma(frame):
    global last_bpm_calculation, current_bpm
    current_time = time.time()

    try:
        value = ser.readline().decode('utf-8', errors='ignore').strip()
        if value.isalpha() or value == '':
            ydata.append(0)
        else:
            ydata.append(float(value))

        ax_electrocardiograma.set_xlim(0, len(ydata))

        if current_time - last_bpm_calculation >= 3:
            if len(ydata) > 15:
                ydata_np = np.array(ydata)
                bpm = calcular_bpm(ydata_np, sampling_rate=66.67)
                if bpm is not None:
                    print(bpm)
                    bpmdata.append(bpm)
                    current_bpm = bpm

            last_bpm_calculation = current_time

    except UnicodeDecodeError:
        print("Error al decodificar datos. Ignorando dato actual.")

    ln.set_data(range(len(ydata)), ydata)
    return ln,

def update_grafica_bpm(frame):
    ax_bpm_grafico.set_xlim(0, len(bpmdata))
    ln2.set_data(range(len(bpmdata)), bpmdata)
    return ln2,

def update_ventana_bpm(frame):
    bpm_text.set_text("BPM: " + str(int(current_bpm)))

    # Cambiar el color del texto dependiendo del valor del BPM
    if current_bpm >= 0 and current_bpm <= 80:
        bpm_text.set_color('#44B4FE')
    elif current_bpm > 80 and current_bpm <= 100:
        bpm_text.set_color('#35d16e')
    elif current_bpm > 100 and current_bpm <= 110:
        bpm_text.set_color('#ffbb00')
    elif current_bpm > 110:
        bpm_text.set_color('#e95569')

    return bpm_text,


if "__main__" == __name__:
    last_bpm_calculation = time.time()
    current_bpm = 0

    try:
        arduino_port = "COM3"
        baud_rate = 115200
        ser = serial.Serial(arduino_port, baud_rate)

        fig_electrocardiograma, ax_electrocardiograma = plt.subplots()
        fig_electrocardiograma.canvas.manager.window.wm_geometry("+0+340")
        ydata = deque(maxlen=150)
        ln, = plt.plot([], [], 'r', label="Valor analógico")

        fig_bpm_grafico, ax_bpm_grafico = plt.subplots()
        fig_bpm_grafico.canvas.manager.window.wm_geometry("+820+340")
        bpmdata = deque(maxlen=150)
        ln2, = plt.plot([], [], 'b', label="BPM")

        fig_ventana_bpm, ax__ventana_bpm = plt.subplots(figsize=(3, 2))
        fig_ventana_bpm.canvas.manager.window.wm_geometry("+0+0")
        ax__ventana_bpm.axis('off')
        bpm_text = plt.text(0.5, 0.5, '', fontsize=30, ha='center')

        ani_electrocardiograma = FuncAnimation(fig_electrocardiograma, update_electrocardiograma, frames=range(0, 100000), init_func=init_electrocardiograma, blit=True, interval=0)
        ani_bpm_grafico = FuncAnimation(fig_bpm_grafico, update_grafica_bpm, frames=range(0, 100000), init_func=init_grafica_bpm, blit=True, interval=0)
        ani_bpm_numerico = FuncAnimation(fig_ventana_bpm, update_ventana_bpm, frames=range(0, 100000), blit=True, interval=0)

        plt.show()

    finally:
        print("Finalizando...")
        ser.close()
