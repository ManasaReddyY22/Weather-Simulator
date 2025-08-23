# assignment_code.py

import numpy as np

class WeatherSimulation:
    def __init__(self, transition_probabilities, holding_times):
        self.transition_probabilities = transition_probabilities
        self.holding_times = holding_times
        self.states = list(transition_probabilities.keys())
        self.current = 'sunny'  # Starting state as 'sunny'
        self.remaining_hours = holding_times[self.current]
        
        # Validate transition probabilities sum to 1 for each state
        for state, transitions in transition_probabilities.items():
            total = sum(transitions.values())
            if not np.isclose(total, 1.0):
                raise RuntimeError(f"Transition probabilities for '{state}' do not sum to 1 (sum={total})")
    
    def get_states(self):
        return self.states
    
    def current_state(self):
        return self.current
    
    def next_state(self):
        if self.remaining_hours > 1:
            self.remaining_hours -= 1
        else:
            transition_probs = self.transition_probabilities[self.current]
            self.current = np.random.choice(self.states, p=list(transition_probs.values()))
            self.remaining_hours = self.holding_times[self.current]
    
    def set_state(self, new_state):
        if new_state not in self.states:
            raise ValueError(f"Invalid state: {new_state}")
        self.current = new_state
        self.remaining_hours = self.holding_times[new_state]
    
    def current_state_remaining_hours(self):
        return self.remaining_hours
    
    def iterable(self):
        while True:
            yield self.current_state()
            self.next_state()
    
    def simulate(self, hours):
        state_counts = {state: 0 for state in self.states}
        for _ in range(hours):
            state_counts[self.current] += 1
            self.next_state()
        total = sum(state_counts.values())
        return [state_counts[state] / total * 100 for state in self.states]

