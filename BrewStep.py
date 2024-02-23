class BrewStep:
    def __init__(self, name=None):
        # Initializer for BrewStep class
        self.name = name
        self.previous_node = None  # Reference to the previous node in the linked list
        self.next_node = None      # Reference to the next node in the linked list

    def __str__(self):
        return self.name
        
