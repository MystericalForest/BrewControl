import TempController

class DataCollector:
    def __init__(self):
        self.temp_controller=TempController.TempController(65)

    def get_temperatur(self):
        return self.temp_controller.get_temperatur()

# Eksempel på brug:
if __name__ == "__main__":
    DataCollector_instance = DataCollector()
    print(DataCollector_instance.get_temperatur())
