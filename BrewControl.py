class Node:
    def __init__(self, data=None):
        self.data = data
        self.next_node = None

class Master:
    def __init__(self):
        self.head = None
        self.active_subclass = None

    def add_subclass(self, data):
        new_node = Node(data)
        new_node.next_node = self.head
        self.head = new_node
        self.active_subclass = new_node

    def switch_active_subclass(self, data):
        current_node = self.head
        while current_node:
            if current_node.data == data:
                self.active_subclass = current_node
                return
            current_node = current_node.next_node

    def display_active_subclass(self):
        if self.active_subclass:
            print("Aktiv underklasse:", self.active_subclass.data)
        else:
            print("Ingen aktiv underklasse.")

# Eksempel på brug:
if __name__ == "__main__":
    master_instance = Master()

    # Tilføj underklasser
    master_instance.add_subclass("Underklasse 1")
    master_instance.add_subclass("Underklasse 2")
    master_instance.add_subclass("Underklasse 3")

    # Vis aktiv underklasse
    master_instance.display_active_subclass()

    # Skift aktiv underklasse
    master_instance.switch_active_subclass("Underklasse 2")

    # Vis igen aktiv underklasse
    master_instance.display_active_subclass()
