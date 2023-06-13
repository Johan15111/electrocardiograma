import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from biosppy.signals import ecg
from collections import deque
import time
import pygame
import threading
import matplotlib.style as style
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button



cmap = ListedColormap(['#000000', '#00FF00'])
cmap2 = ListedColormap(['#000000', '#EB0933'])


paused = False



style.use('ggplot')


# Inicializa Pygame y carga el sonido
pygame.mixer.init()
beep_sound = pygame.mixer.Sound("beep1.wav")

# Crear una Lock para la sincronización de threads
beep_lock = threading.Lock()

# Ajusta el umbral de acuerdo a tus necesidades
thresh = 100

plt.rcParams['toolbar'] = 'None' 
plt.rcParams['keymap.fullscreen'] = [] 
plt.rcParams['keymap.home'] = [] 
plt.rcParams['keymap.save'] = [] 
plt.rcParams['keymap.zoom'] = [] 

def play_beep():
    # Adquiere la Lock antes de reproducir el sonido
    with beep_lock:
        beep_sound.play()

def init_electrocardiograma():
    ax_electrocardiograma.set_facecolor(background_color)

    ax_electrocardiograma.set_facecolor('black')
    ax_electrocardiograma.set_ylim(-70, 200)
    ax_electrocardiograma.set_title("Electrocardiograma en vivo", color='white')
    ax_electrocardiograma.set_ylabel("microvoltios", color='white')
    ax_electrocardiograma.set_xticklabels([]) 
    ax_electrocardiograma.grid(True, color='white',alpha=0.1)
    ln.set_color(cmap(1))  # Establece el color verde más vivo para la línea
    return ln,



def init_grafica_bpm():
    ax_bpm_grafico.set_facecolor(background_color)

    ax_bpm_grafico.set_facecolor('black')
    ax_bpm_grafico.set_ylim(0, 200)
    ax_bpm_grafico.set_title("Latidos por minuto en vivo", color='white')
    ax_bpm_grafico.set_ylabel("BPM", color='white')
    ax_bpm_grafico.set_xticklabels([]) 
    ax_bpm_grafico.grid(True, color='white',alpha=0.1)
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
    global last_bpm_calculation, current_bpm, last_beep_time
    current_time = time.time()

    try:
        value = ser.readline().decode('utf-8', errors='ignore').strip()
        if value.isalpha() or value == '':
            ydata.append(0)
        else:
            ydata.append(float(value))

        ax_electrocardiograma.set_xlim(0, len(ydata))

        if ydata[-1] > thresh and (current_time - last_beep_time > 0.5):
            threading.Thread(target=play_beep).start()
            last_beep_time = current_time

        if current_time - last_bpm_calculation >= 3:
            if len(ydata) > 15:
                ydata_np = np.array(ydata)
                bpm = calcular_bpm(ydata_np, sampling_rate=66.67)
                if bpm is not None:
                    #print(bpm)
                    bpmdata.append(bpm)
                    current_bpm = bpm

            last_bpm_calculation = current_time

    except UnicodeDecodeError:
        print("Error al decodificar datos. Ignorando dato actual.")

    ln.set_data(range(len(ydata)), ydata)
    ln.set_color(cmap(1))  # Establece el color verde más vivo para los datos
    return ln,

def update_grafica_bpm(frame):
    ax_bpm_grafico.set_xlim(0, len(bpmdata))
    ln2.set_data(range(len(bpmdata)), bpmdata)
    ln2.set_color(cmap2(1))
    return ln2,

def update_ventana_bpm(frame):
    bpm_text.set_text("BPM: " + str(int(current_bpm)))

    if current_bpm >= 0 and current_bpm <= 80:
        bpm_text.set_color('#44B4FE')
    elif current_bpm > 80 and current_bpm <= 100:
        bpm_text.set_color('#35d16e')
    elif current_bpm > 100 and current_bpm <= 110:
        bpm_text.set_color('#ffbb00')
    elif current_bpm > 110:
        bpm_text.set_color('#e95569')

    return bpm_text,

def pause_animation(event):
    global paused
    paused = not paused
    if paused:
        ani_electrocardiograma.event_source.stop()
        ani_bpm_grafico.event_source.stop()
        ani_bpm_numerico.event_source.stop()
    else:
        ani_electrocardiograma.event_source.start()
        ani_bpm_grafico.event_source.start()
        ani_bpm_numerico.event_source.start()


if __name__ == "__main__":
    last_bpm_calculation = time.time()
    current_bpm = 0
    last_beep_time = 0

    try:
        arduino_port = "COM3"
        baud_rate = 115200
        ser = serial.Serial(arduino_port, baud_rate)

        background_color = '#333333'

        fig, (ax_electrocardiograma, ax_bpm_grafico, ax__ventana_bpm) = plt.subplots(3, 1, figsize=(10, 15))

        fig.patch.set_facecolor(background_color)

        fig.canvas.manager.set_window_title('CARDUINO')


        fig.canvas.manager.window.wm_geometry("+350+0")

        ydata = deque(maxlen=100)
        ln, = ax_electrocardiograma.plot([], [], 'r', label="Valor analógico")

        bpmdata = deque(maxlen=100)
        ln2, = ax_bpm_grafico.plot([], [], 'b', label="BPM")


        ax__ventana_bpm.axis('off')
        bpm_text = ax__ventana_bpm.text(0.5, 0.5, '', fontsize=30, ha='center')



        ani_electrocardiograma = FuncAnimation(fig, update_electrocardiograma, frames=range(0, 100000), init_func=init_electrocardiograma, blit=True, interval=0)
        ani_bpm_grafico = FuncAnimation(fig, update_grafica_bpm, frames=range(0, 100000), init_func=init_grafica_bpm, blit=True, interval=0)
        ani_bpm_numerico = FuncAnimation(fig, update_ventana_bpm, frames=range(0, 100000), blit=True, interval=0)

        pause_button_ax = fig.add_axes([0.435, 0.15, 0.15, 0.05])  # Ajusta la posición y tamaño del botón
        pause_button = Button(pause_button_ax, 'Pausa/Reanudar')
        pause_button.on_clicked(pause_animation)
        

        plt.show()

    finally:
        print("Finalizando...")
        ser.close()