import BrewStep
from enum import Enum

class Brew_status(Enum):
    NOT_STARTED = 1
    STARTED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5

class BrewController:
    def __init__(self):
        # Initializer for BrewController class
        self.first = None           # Reference to the first node in the linked list
        self.last = None            # Reference to the last node in the linked list
        self.active_brew_step = None     # Reference to the currently active step
        self.status=Brew_status.NOT_STARTED
        self.generate_brew_control_default_data()  # Generate default brewing steps

    def add_brew_step(self, name):
        # Adds a new BrewStep to the linked list
        new_node = BrewStep.BrewStep(name)
        if (self.first is None):
            # If the list is empty, set the new node as the first node
            self.first = new_node
        new_node.previous_node = self.last
        if (self.last is not None):
            # If there is a last node, set its next_node to the new node
            self.last.next_node = new_node
        self.last = new_node         # Update last to the new node
        self.active_brew_step = new_node  # Set the active step to the new node

    def switch_active_brew_step(self, name):
        # Finds and sets the active step to the one with the given name
        current_node = self.first
        while current_node:
            if current_node.name == name:
                self.active_step = current_node
                return
            current_node = current_node.next_node

    def display_all_brew_step(self):
        # Prints the names of all brew steps in the linked list
        current_node = self.first
        while current_node:
            print("Brew Step:", current_node.name)
            current_node = current_node.next_node

    def next_brew_step(self):
        # Moves the active step to the next step in the linked list
        if self.active_brew_step is not None:
            self.active_brew_step = self.active_brew_step.next_node

    def start_brew(self):
        self.status=Brew_status.STARTED

    def get_status(self):
        if (self.status==Brew_status.NOT_STARTED):
            return "Not started"
        if (self.status==Brew_status.STARTED):
            return "Started"
        if (self.status==Brew_status.PAUSED):
            return "Paused"
        if (self.status==Brew_status.STOPPED):
            return "Stopped"
        return "Error"
        
    def get_active_brew_step_name(self):
        # Returns the name of the currently active brew step
        if self.active_brew_step:
            return self.active_brew_step.name
        else:
            return "No active brew steps."

    def __len__(self):
        # Returns the number of steps in the Brew Controller
        current_node = self.first
        count=0
        while current_node:
            count+=1
            current_node = current_node.next_node
        return count
            
    def generate_brew_control_default_data(self):
        # Initializes the linked list with default brewing steps and sets the active step to the first step
        self.add_brew_step("Step 1")
        self.add_brew_step("Step 2")
        self.add_brew_step("Step 3")
        self.add_brew_step("Step 4")
        self.active_brew_step = self.first

# Eksempel på brug:
if __name__ == "__main__":
    BrewController_instance = BrewController()

    # Vis aktiv underklasse
    print(BrewController_instance.active_brew_step)

    # Skift aktiv underklasse
    BrewController_instance.next_brew_step()
    BrewController_instance.next_brew_step()

    # Vis igen aktiv underklasse
    print(BrewController_instance.active_brew_step)

    # Vis alle underklasser
    print()
    BrewController_instance.display_all_brew_step()
