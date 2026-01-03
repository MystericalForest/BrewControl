import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QDialog, QLineEdit, 
                             QDoubleSpinBox, QFormLayout, QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import deque

class ParameterDialog(QDialog):
    def __init__(self, names, setpoints, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Parametre')
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.name_inputs = []
        self.setpoint_inputs = []
        
        for i in range(3):
            name_input = QLineEdit(names[i])
            setpoint_input = QDoubleSpinBox()
            setpoint_input.setRange(-50, 100)
            setpoint_input.setValue(setpoints[i])
            setpoint_input.setSuffix('°C')
            
            self.name_inputs.append(name_input)
            self.setpoint_inputs.append(setpoint_input)
            
            layout.addRow(f'Navn {i+1}:', name_input)
            layout.addRow(f'Sætpunkt {i+1}:', setpoint_input)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('OK')
        cancel_btn = QPushButton('Annuller')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def get_values(self):
        names = [inp.text() for inp in self.name_inputs]
        setpoints = [inp.value() for inp in self.setpoint_inputs]
        return names, setpoints

class AlarmLogDialog(QDialog):
    def __init__(self, alarm_log, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Alarm Log')
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Courier', 10))
        
        # Vis alarm log
        log_content = "\n".join(alarm_log) if alarm_log else "Ingen alarmer endnu"
        self.log_text.setPlainText(log_content)
        
        layout.addWidget(QLabel('Alarm Historie:'))
        layout.addWidget(self.log_text)
        
        close_btn = QPushButton('Luk')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class ParameterLogDialog(QDialog):
    def __init__(self, param_log, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Parameter Log')
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Courier', 10))
        
        log_content = "\n".join(param_log) if param_log else "Ingen parameter ændringer endnu"
        self.log_text.setPlainText(log_content)
        
        layout.addWidget(QLabel('Parameter Historie:'))
        layout.addWidget(self.log_text)
        
        close_btn = QPushButton('Luk')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class GraphDialog(QDialog):
    def __init__(self, names, temp_history, setpoint_history, alarm_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Temperatur Grafer')
        self.resize(800, 600)
        self.parent_app = parent
        
        layout = QVBoxLayout()
        
        # Tab widget for hver temperatur
        self.tabs = QTabWidget()
        self.canvases = []
        self.axes = []
        
        for i in range(3):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Matplotlib figur
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            
            self.canvases.append(canvas)
            self.axes.append(ax)
            
            tab_layout.addWidget(canvas)
            tab.setLayout(tab_layout)
            self.tabs.addTab(tab, names[i])
        
        layout.addWidget(self.tabs)
        
        close_btn = QPushButton('Luk')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Timer til opdatering af grafer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graphs)
        self.update_timer.start(2000)
        
        self.update_graphs()
    
    def update_graphs(self):
        if not self.parent_app:
            return
            
        for i in range(3):
            ax = self.axes[i]
            ax.clear()
            
            temp_history = self.parent_app.temp_history[i]
            setpoint_history = self.parent_app.setpoint_history[i]
            alarm_history = self.parent_app.alarm_history[i]
            
            if len(temp_history) > 0:
                times = list(range(len(temp_history)))
                temps = list(temp_history)
                setpoints = list(setpoint_history)
                alarms = list(alarm_history)
                
                # Plot kontinuerlig temperaturlinje med segmenter
                for j in range(len(times) - 1):
                    x_seg = [times[j], times[j + 1]]
                    y_seg = [temps[j], temps[j + 1]]
                    
                    if alarms[j] or alarms[j + 1]:  # Hvis et af punkterne er i alarm
                        ax.plot(x_seg, y_seg, 'r-', linewidth=3)
                    else:
                        ax.plot(x_seg, y_seg, 'g-', linewidth=2)
                
                # Tilføj stjerner kun for alarm start/stop
                alarm_events = self.parent_app.alarm_events[i]
                events = list(alarm_events)
                
                start_times = [t for t, e in zip(times, events) if e == 'start']
                start_temps = [temp for temp, e in zip(temps, events) if e == 'start']
                if start_times:
                    ax.scatter(start_times, start_temps, marker='*', s=150, color='red', 
                              label='Alarm START', zorder=5)
                
                stop_times = [t for t, e in zip(times, events) if e == 'stop']
                stop_temps = [temp for temp, e in zip(temps, events) if e == 'stop']
                if stop_times:
                    ax.scatter(stop_times, stop_temps, marker='*', s=150, color='green', 
                              label='Alarm STOP', zorder=5)
                
                # Plot sætpunkt
                ax.plot(times, setpoints, 'b--', label='Sætpunkt', linewidth=2)
                
                # Normal område
                ax.fill_between(times, 
                               [sp - 2 for sp in setpoints], 
                               [sp + 2 for sp in setpoints], 
                               alpha=0.2, color='lightgreen', label='Normal område')
                
                # Tilføj legend labels manuelt
                ax.plot([], [], 'g-', label='Temperatur (Normal)', linewidth=2)
                ax.plot([], [], 'r-', label='Temperatur (ALARM)', linewidth=3)
            
            ax.set_title(f'{self.parent_app.names[i]} - Temperatur over tid')
            ax.set_xlabel('Tid (målinger)')
            ax.set_ylabel('Temperatur (°C)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self.canvases[i].draw()
    
    def closeEvent(self, event):
        self.update_timer.stop()
        event.accept()

class TemperaturApp(QWidget):
    def __init__(self):
        super().__init__()
        self.names = ['Stue', 'Køkken', 'Soveværelse']
        self.setpoints = [22.0, 21.0, 20.0]
        self.temperatures = [22.5, 21.8, 20.2]
        self.alarm_states = [False, False, False]
        self.alarm_log = []
        self.param_log = []
        
        # Historik for grafer (max 100 punkter)
        self.temp_history = [deque(maxlen=100) for _ in range(3)]
        self.setpoint_history = [deque(maxlen=100) for _ in range(3)]
        self.alarm_history = [deque(maxlen=100) for _ in range(3)]
        self.alarm_events = [deque(maxlen=100) for _ in range(3)]  # Kun alarm start/stop
        
        # Initialiser historik
        for i in range(3):
            self.temp_history[i].append(self.temperatures[i])
            self.setpoint_history[i].append(self.setpoints[i])
            self.alarm_history[i].append(False)
            self.alarm_events[i].append(None)  # None = ingen ændring
        
        self.initUI()
        
        # Timer til simulering af temperaturændringer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_temperatures)
        self.timer.start(2000)
    
    def initUI(self):
        self.setWindowTitle('Temperatur Display')
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Knapper
        button_layout1 = QHBoxLayout()
        param_btn = QPushButton('Parametre')
        param_btn.clicked.connect(self.open_parameters)
        param_log_btn = QPushButton('Parameter Log')
        param_log_btn.clicked.connect(self.open_parameter_log)
        button_layout1.addWidget(param_btn)
        button_layout1.addWidget(param_log_btn)
        
        button_layout2 = QHBoxLayout()
        alarm_log_btn = QPushButton('Alarm Log')
        alarm_log_btn.clicked.connect(self.open_alarm_log)
        graph_btn = QPushButton('Grafer')
        graph_btn.clicked.connect(self.open_graphs)
        button_layout2.addWidget(alarm_log_btn)
        button_layout2.addWidget(graph_btn)
        
        layout.addLayout(button_layout1)
        layout.addLayout(button_layout2)
        
        # Font til temperaturer
        font = QFont('Arial', 14, QFont.Bold)
        
        # Tre temperatur labels
        self.temp_labels = []
        for i in range(3):
            label = QLabel()
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(50)
            self.temp_labels.append(label)
            layout.addWidget(label)
        
        self.setLayout(layout)
        self.update_display()
    
    def update_temperatures(self):
        # Simuler temperaturændringer
        for i in range(3):
            old_alarm = self.alarm_states[i]
            self.temperatures[i] += random.uniform(-0.5, 0.5)
            
            # Tilføj til historik
            self.temp_history[i].append(self.temperatures[i])
            self.setpoint_history[i].append(self.setpoints[i])
            
            # Check alarm status
            alarm = abs(self.temperatures[i] - self.setpoints[i]) > 2.0
            self.alarm_history[i].append(alarm)
            
            # Registrer kun alarm ændringer
            if alarm and not old_alarm:
                self.alarm_events[i].append('start')  # Alarm starter
            elif not alarm and old_alarm:
                self.alarm_events[i].append('stop')   # Alarm stopper
            else:
                self.alarm_events[i].append(None)    # Ingen ændring
        
        self.update_display()
    
    def update_display(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for i, label in enumerate(self.temp_labels):
            temp = self.temperatures[i]
            setpoint = self.setpoints[i]
            name = self.names[i]
            
            # Check for alarm (mere end 2 grader fra sætpunkt)
            alarm = abs(temp - setpoint) > 2.0
            
            # Log alarm state changes
            if alarm and not self.alarm_states[i]:
                # Alarm started
                self.alarm_states[i] = True
                deviation = temp - setpoint
                log_entry = f'{current_time} - ALARM START: {name} ({temp:.1f}°C, afvigelse: {deviation:+.1f}°C)'
                self.alarm_log.append(log_entry)
            elif not alarm and self.alarm_states[i]:
                # Alarm cleared
                self.alarm_states[i] = False
                log_entry = f'{current_time} - ALARM CLEAR: {name} ({temp:.1f}°C, normaliseret)'
                self.alarm_log.append(log_entry)
            
            text = f'{name}: {temp:.1f}°C (Sæt: {setpoint:.1f}°C)'
            if alarm:
                text += ' ⚠️ ALARM'
                label.setStyleSheet('background-color: red; color: white; padding: 10px;')
            else:
                label.setStyleSheet('background-color: lightgreen; padding: 10px;')
            
            label.setText(text)
    
    def open_parameters(self):
        old_names = self.names.copy()
        old_setpoints = self.setpoints.copy()
        
        dialog = ParameterDialog(self.names, self.setpoints, self)
        if dialog.exec_() == QDialog.Accepted:
            new_names, new_setpoints = dialog.get_values()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Log ændringer
            for i in range(3):
                if old_names[i] != new_names[i]:
                    log_entry = f'{current_time} - NAVN ÆNDRET: "{old_names[i]}" -> "{new_names[i]}"'
                    self.param_log.append(log_entry)
                
                if old_setpoints[i] != new_setpoints[i]:
                    log_entry = f'{current_time} - SÆTPUNKT ÆNDRET: {old_names[i]} {old_setpoints[i]:.1f}°C -> {new_setpoints[i]:.1f}°C'
                    self.param_log.append(log_entry)
            
            self.names, self.setpoints = new_names, new_setpoints
            self.update_display()
    
    def open_alarm_log(self):
        dialog = AlarmLogDialog(self.alarm_log, self)
        dialog.exec_()
    
    def open_parameter_log(self):
        dialog = ParameterLogDialog(self.param_log, self)
        dialog.exec_()
    
    def open_graphs(self):
        dialog = GraphDialog(self.names, self.temp_history, self.setpoint_history, self.alarm_history, self)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TemperaturApp()
    window.show()
    sys.exit(app.exec_())