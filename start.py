import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

# Generer nogle tilfældige data
x_data = np.linspace(0, 10, 100)
y_data = np.sin(x_data)

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brew Control")
        self.root.configure(bg="#2E2E2E")  # Baggrundsfarve for mørkt tema

        # Opretter et Matplotlib-plot
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.plot(x_data, y_data, color='lightblue')
        self.ax.set_xlabel('X-akse', color='white')
        self.ax.set_ylabel('Y-akse', color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.set_facecolor('#2E2E2E')  # Baggrundsfarve for mørkt tema

        self.fig.patch.set_facecolor('#2E2E2E')  # Baggrundsfarve for mørkt tema
        
        # Indsætter Matplotlib-plot i Tkinter-vinduet
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg="#2E2E2E")  # Baggrundsfarve for mørkt tema

        # Placerer Matplotlib-plot i bunden af vinduet og lader det fylde bredden
        self.canvas_widget.grid(row=3, column=0, rowspan=2, sticky="nsew")

        # Konfigurerer vinduets rækker og kolonner for at skalere korrekt
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Label-felter over Matplotlib-plot
        label1 = ttk.Label(self.root, text="43 min", font=("Helvetica", 24), background="#2E2E2E", foreground="white")
        label2 = ttk.Label(self.root, text="Mæskning", font=("Helvetica", 18), background="#2E2E2E", foreground="white")
        label3 = ttk.Label(self.root, text="Næste opgave: Tilsæt humle", font=("Helvetica", 12), background="#2E2E2E", foreground="white")

        # Placerer label-felter over Matplotlib-plot
        label1.grid(row=0, column=0, pady=(10, 0))
        label2.grid(row=1, column=0, pady=(10, 0))
        label3.grid(row=2, column=0, pady=(10, 0))

        # Opdaterer baggrundsfarven for resten af Tkinter-vinduet
        self.root.tk_setPalette(background="#2E2E2E", foreground="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.geometry("800x600")
    root.mainloop()
