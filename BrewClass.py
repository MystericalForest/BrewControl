import BrewController
from datetime import date
from enum import Enum
import StepsClass

class Brew_status(Enum):
    NOT_STARTED = 1
    STARTED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5
    
class BrewClass:
    def __init__(self, steps, name=None):
        # Initializer for BrewStep class
        self.name = name
        self.steps = steps
        self.brewdate=None
        self.status=Brew_status.NOT_STARTED
        self.brew_controller = BrewController.BrewController(self.steps)

    def __str__(self):
        return self.name + ": " + self.get_status() + " - " + str(self.brew_controller.active_brew_step)

    def start_brew(self):
        self.brew_controller.start_brew()
        if self.brewdate is None:
            self.brewdate=date.today()

    def stop_brew(self):
        self.brew_controller.stop_brew()

    def pause_brew(self):
        self.brew_controller.pause_brew()

    def reset_brew(self):
        self.brew_controller.reset_brew()

    def restart_brew(self):
        self.brew_controller.reset_brew()
        self.brew_controller.start_brew()

    def next_brew_step(self):
        self.brew_controller.next_brew_step()
        
    def get_status(self):
        return self.brew_controller.get_status()

    def get_set_point_data(self):
        return self.brew_controller.get_set_point_data()

    def get_logger_data(self):
        return self.brew_controller.get_logger_data()

    def get_tast_times(self):
        return self.brew_controller.get_tast_times()

    def get_current_step_text(self):
        return "Mæskning"

    def get_next_task_text(self):
        return "Næste opgave: Tilsæt humle"

    def get_x_axis_min(self):
        return self.brew_controller.get_x_axis_min()

    def get_x_axis_max(self):
        return self.brew_controller.get_x_axis_max()

    def update_data(self):
        return self.brew_controller.update_data()

    def get_current_timestamp(self):
        return self.brew_controller.get_current_timestamp()

# Eksempel på brug:
if __name__ == "__main__":
    BrewClass_instance = BrewClass("Bryg 1")
    print(BrewClass_instance)
    BrewClass_instance.start_brew()
    print(BrewClass_instance)
