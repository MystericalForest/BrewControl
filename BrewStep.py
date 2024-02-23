from enum import Enum

class Brew_step_status(Enum):
    NOT_STARTED = 1
    STARTED = 2
    PAUSED = 3
    AWAITING = 4
    STOPPED = 5
    ENDED = 6
    ERROR = 7
    
class BrewStep:
    def __init__(self, name=None):
        # Initializer for BrewStep class
        self.name = name
        self.previous_node = None  # Reference to the previous node in the linked list
        self.status=Brew_step_status.NOT_STARTED
        self.next_node = None      # Reference to the next node in the linked list

    def __str__(self):
        return self.name + " - " + self.get_status()

    def start_brew_step(self):
        if (self.status==Brew_step_status.NOT_STARTED
            or self.status==Brew_step_status.PAUSED
            or self.status==Brew_step_status.STOPPED):
            self.status=Brew_step_status.STARTED

    def stop_brew_step(self):
        if (self.status==Brew_step_status.STARTED
            or self.status==Brew_step_status.PAUSED):
            self.status=Brew_step_status.STOPPED

    def pause_brew_step(self):
        if self.status==Brew_step_status.STARTED:
            self.status=Brew_step_status.PAUSED

    def reset_brew_step(self):
        self.status=Brew_step_status.NOT_STARTED

    def get_status(self):
        if (self.status==Brew_step_status.NOT_STARTED):
            return "Not started"
        if (self.status==Brew_step_status.STARTED):
            return "Started"
        if (self.status==Brew_step_status.PAUSED):
            return "Paused"
        if (self.status==Brew_step_status.AWAITING):
            return "Awaiting"
        if (self.status==Brew_step_status.STOPPED):
            return "Stopped"
        if (self.status==Brew_step_status.ENDED):
            return "Ended"
        return "Error"
        
