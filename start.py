import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import random
import BrewClass

class Brew_GUI:
    def __init__(self, root):
        self.BrewClass_instance=BrewClass.BrewClass()
        self.is_brewing=False
        self.root = root
        self.root.title("Brew Control")
        self.root.configure(bg="#2E2E2E")  # Baggrundsfarve for mørkt tema

        # Opretter et Matplotlib-plot
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_xlabel('Tid', color='white')
        self.ax.set_ylabel('Temperatur', color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.set_facecolor('#2E2E2E')  # Baggrundsfarve for mørkt tema

        self.fig.patch.set_facecolor('#2E2E2E')  # Baggrundsfarve for mørkt tema
        
        # Indsætter Matplotlib-plot i Tkinter-vinduet
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg="#2E2E2E")  # Baggrundsfarve for mørkt tema

        # Placerer Matplotlib-plot i bunden af vinduet og lader det fylde bredden
        self.canvas_widget.grid(row=3, column=0, rowspan=2, columnspan=2, sticky="nsew")

        # Konfigurerer vinduets rækker og kolonner for at skalere korrekt
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Label-felter over Matplotlib-plot
        self.label_time = ttk.Label(self.root, text="43 min", font=("Helvetica", 24), background="#2E2E2E", foreground="white")
        label2 = ttk.Label(self.root, text="Mæskning", font=("Helvetica", 18), background="#2E2E2E", foreground="white")
        label3 = ttk.Label(self.root, text="Næste opgave: Tilsæt humle", font=("Helvetica", 12), background="#2E2E2E", foreground="white")

        # Placerer label-felter over Matplotlib-plot
        self.label_time.grid(row=0, column=0, pady=(10, 0))
        label2.grid(row=1, column=0, pady=(10, 0))
        label3.grid(row=2, column=0, pady=(10, 0))

        # Knapper
        self.button_start_brew = ttk.Button(self.root, text="Start Brygning", command=self.button_start_brew_callback)
        button_2 = ttk.Button(self.root, text="Knap 2")
        button_3 = ttk.Button(self.root, text="Knap 3")

        # Placerer Knapperne
        self.button_start_brew.grid(row=0, column=1, pady=(10, 0), sticky="w")
        button_2.grid(row=1, column=1, pady=(10, 0), sticky="w")
        button_3.grid(row=2, column=1, pady=(10, 0), sticky="w")

        # Opdaterer baggrundsfarven for resten af Tkinter-vinduet
        self.root.tk_setPalette(background="#2E2E2E", foreground="white")

        # Opdater data visninger
        self.update_data()

    def update_data(self):
        self.BrewClass_instance.update_data()

        # Opdater plotlinjerne med de nye data
        self.ax.clear()
        sp_x, sp_y = self.BrewClass_instance.get_set_point_data()
        self.ax.plot(sp_x, sp_y, marker='', linestyle='-', color='lightblue', label='Sætpunkt')
        temp_x, temp_y = self.BrewClass_instance.get_logger_data()
        self.ax.plot(temp_x, temp_y, marker='o', linestyle='-', color='darksalmon', label='Temperatur')
        for task in self.BrewClass_instance.get_tast_times():
            self.ax.plot([task, task], [0,90], marker='', linestyle=':', color='darksalmon', label='Task')

        # Juster aksen for at inkludere de nye data
        self.ax.set_xlim(self.BrewClass_instance.get_x_axis_min(), self.BrewClass_instance.get_x_axis_max())

        # Opdatér Matplotlib-figuren
        self.canvas.draw()

        # Opdatér Label felterne
        time_text=str(self.BrewClass_instance.get_current_timestamp()) + " min"
        if not (self.is_brewing):
            time_text=time_text+" (Pause)"
        self.label_time.configure(text=time_text)

        if (self.is_brewing):
            # Planlæg næste opdatering efter 1000 ms (1 sekund)
            self.root.after(1000, self.update_data)

    def button_start_brew_callback(self):
        if self.is_brewing:
            self.button_start_brew.configure(text="Start Brygning")
            self.stop_automatic_update()
        else:
            self.button_start_brew.configure(text="Pause Brygning")
            self.start_automatic_update()

    def start_automatic_update(self):
        self.is_brewing=True
        self.update_data()

    def stop_automatic_update(self):
        self.is_brewing=False
        
    def on_closing(self):
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Brew_GUI(root)
    root.geometry("800x600")

    # Bind on_closing-funktionen til vinduets lukningsbegivenhed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
