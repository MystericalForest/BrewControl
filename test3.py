import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

# Startdata
x_data_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
x_data_2 = [1, 2, 3, 4, 5]
y_setpoints = [65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85]
y_temperatures = [55, 60, 68, 62, 66]

# Tilpas Matplotlib til et mørkt tema
plt.style.use('dark_background')

class GraphUpdater:
    def __init__(self, ax):
        self.ax = ax
        
    def update_data(self):
        # Simulér opdatering af data
        if len(y_setpoints)>x_data_2[-1]:
            set_punkt=y_setpoints[x_data_2[-1]]
        else:
            set_punkt=y_setpoints[-1]
        new_temperature = random.randint(set_punkt-3, set_punkt+3)

        # Tilføj de nye data til listen
        x_data_2.append(x_data_2[-1] + 1)
        #y_setpoints.append(new_setpoint)
        y_temperatures.append(new_temperature)

        # Opdater plotlinjerne med de nye data
        self.ax.clear()
        self.ax.plot(x_data_1, y_setpoints, marker='', linestyle='-', color='blue', label='Sætpunkt')
        self.ax.plot(x_data_2, y_temperatures, marker='o', linestyle='-', color='red', label='Temperatur')

        # Juster aksen for at inkludere de nye data
        self.ax.legend()
        self.ax.set_xlim(min(min(x_data_1),min(x_data_2)), max(max(x_data_1), max(x_data_2)))

        # Opdatér Matplotlib-figuren
        canvas.draw()

        # Planlæg næste opdatering efter 1000 ms (1 sekund)
        window.after(1000, self.update_data)

def on_manual_update():
    graph_updater.update_data()

def on_closing():
    window.quit()
    window.destroy()

# Opret hovedvinduet
window = tk.Tk()
window.title("Automatisk opdatering af graf")
window.configure(bg='black')  # Baggrundsfarve for Tkinter-vinduet

# Opret faner
notebook = ttk.Notebook(window)

# Opret fane 1
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Brew date')

# Opret fane 2 med grafen
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Graf')

# Opret fane 3
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Fane 3')

notebook.pack(expand=1, fill='both')

# Opret en figur og en akse
fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
fig.patch.set_facecolor('black')  # Baggrundsfarve for Matplotlib-figuren

# Plot sætpunkter
ax.plot(x_data_1, y_setpoints, marker='', linestyle='-', color='blue', label='Sætpunkter')

# Plot temperaturer
ax.plot(x_data_2, y_temperatures, marker='o', linestyle='-', color='red', label='Temperaturer')

# Tilføj en legend
ax.legend()

# Opret et lærred til Tkinter
canvas = FigureCanvasTkAgg(fig, master=tab2)
canvas.draw()

# Placér lærredet i Tkinter-vinduet
canvas.get_tk_widget().pack()

# Opret en instans af GraphUpdater
graph_updater = GraphUpdater(ax)

# Opret en knap til manuel opdatering
update_button = ttk.Button(tab1, text="Opdater graf manuelt", command=on_manual_update, style='TButton')
update_button.pack()

# Planlæg første automatiske opdatering efter 1000 ms (1 sekund)
window.after(1000, graph_updater.update_data)

# Bind on_closing-funktionen til vinduets lukningsbegivenhed
window.protocol("WM_DELETE_WINDOW", on_closing)

# Tilpas Ttk-stil for knapper
style = ttk.Style()
style.configure('TButton', background='black', foreground='white')

# Start Tkinter-loop
window.mainloop()
