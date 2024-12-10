import json
import os

class Flash:
    def __init__(self, state_file="resources/state.json"):
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"flash": 1}

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f)

    def toggle(self):
        self.state["flash"] = 1 - self.state["flash"]
        self.save_state()
        flash_state = "on" if self.state["flash"] else "off"
        print(f"Flash toggled {flash_state}")

    def is_on(self):
        return self.state["flash"] == 1
