import BrewController
from enum import Enum

class Brew_status(Enum):
    NOT_STARTED = 1
    STARTED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5
    
class BrewClass:
    def __init__(self, name=None):
        # Initializer for BrewStep class
        self.name = name
        self.status=Brew_status.NOT_STARTED
        self.brew_controller = BrewController.BrewController()

    def __str__(self):
        return self.name + ": " + self.get_status() + " - " + str(self.brew_controller.active_brew_step)

    def start_brew(self):
        self.brew_controller.start_brew()

    def get_status(self):
        return self.brew_controller.get_status()

# Eksempel på brug:
if __name__ == "__main__":
    BrewClass_instance = BrewClass("Bryg 1")
    print(BrewClass_instance)
    BrewClass_instance.start_brew()
    print(BrewClass_instance)
