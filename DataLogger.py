import TempController
import threading
import time

class DataLogger(threading.Thread):
    def __init__(self, interval, target_class):
        threading.Thread.__init__(self)
        self.interval = interval
        self.x_values=[]
        self.y_values=[]
        self.target_class = target_class
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            # Opret en ny instans af target_class og kald dens metode
            instance = self.target_class(65)
            self.x_values.append(len(self.x_values)+1)
            self.y_values.append(instance.get_temperatur())
            time.sleep(self.interval)

    def stop(self):
        self.stop_event.set()

if __name__ == "__main__":
    target_class = TempController.TempController
    interval = 1  # Sekund

    logger_thread = DataLogger(interval, target_class)
    logger_thread.start()

    try:
        while True:
            print(logger_thread.x_values)
            print(logger_thread.y_values)
            time.sleep(1)
    except KeyboardInterrupt:
        logger_thread.stop()
        logger_thread.join()
