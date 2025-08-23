# test.py

from assignment_code import WeatherSimulation
import numpy as np
import sys

print('\n*****************************')
print('Testing Assignment 2, DV1614')
print('*****************************')

# Check Python version
if sys.version_info < (3, 7, 0):
    print('\nYour python version info is:', sys.version_info)
    sys.exit("Python version should be equal or bigger than 3.7.0")
else:
    print(f'\nYour python version is correct ({sys.version_info})')

def calculate_embedded_steady_state(transition_matrix):
    """Calculate steady-state probabilities for the embedded Markov chain."""
    n = len(transition_matrix)
    A = np.append(transition_matrix.T - np.eye(n), [np.ones(n)], axis=0)
    b = np.append(np.zeros(n), [1])
    return np.linalg.lstsq(A, b, rcond=None)[0]

def calculate_true_steady_state(pi_embed, holding_times):
    """Calculate true steady-state probabilities considering holding times."""
    h = np.array([holding_times[state] for state in states])
    pi_true = pi_embed * h
    pi_true /= pi_true.sum()
    return pi_true

def check_formalities(transitions, holding_time):
    ITERATING_ROUNDS = 10000

    # Check creating WeatherSimulation
    try:
        weather_sim = WeatherSimulation(transitions, holding_time)
    except Exception as e:
        print(f'ERROR! Error in creating WeatherSimulation object: {e}')
        sys.exit('NOK!')

    # Check methods
    methods = ['get_states', 'set_state', 'current_state', 'current_state_remaining_hours', 'next_state', 'iterable', 'simulate']
    if not all(map(lambda x: hasattr(weather_sim, x) and callable(getattr(weather_sim, x)), methods)):
        print('ERROR! Not all methods have been implemented.')
        sys.exit('NOK!')

    # Check iterables without printing every state
    print(f'\nTesting iterating (for {ITERATING_ROUNDS} rounds):')
    try:
        sim_iter = weather_sim.iterable()
        for i in range(ITERATING_ROUNDS):
            next(sim_iter)
    except Exception as e:
        print(f'ERROR! Problem in iterating: {e}')
        sys.exit('NOK!')

def check_exception(wrong_transitions, holding_time):
    print(f'\nCheck exception handling')
    try:
        weather_sim = WeatherSimulation(wrong_transitions, holding_time)
    except RuntimeError as err:
        print(f'Exception raised (correctly) with details: {err}')
        return True
    except Exception as e:
        print(f'Exception raised but not with RuntimeError: {e}')
        return False
    return False

def check_holding_times(transitions, holding_time):
    print(f'\nCheck holding times')

    NUM_CHANGES = 20

    weather_sim = WeatherSimulation(transitions, holding_time)

    for i in range(NUM_CHANGES):
        last_state = weather_sim.current_state()
        hd = holding_time[last_state]
        for j in range(hd):
            if weather_sim.current_state() != last_state:
                print(f'Error: State {last_state} changed before holding time {hd} to {weather_sim.current_state()}!')
                return False
            weather_sim.next_state()
    return True

def run_test(transitions, holding_time, pi_true, tolerance):
    STATES = list(transitions.keys())
    HOURS = 10000

    weather_sim = WeatherSimulation(transitions, holding_time)

    # Test simulation
    print(f'\nTesting simulation function for {HOURS} hours:')
    freq = weather_sim.simulate(HOURS)
    print(f'Simulation resulted in {list(zip(STATES, freq))}')

    # Check if the percentages add up to 100
    if not np.isclose(np.sum(freq), 100.0):
        sys.exit('ERROR! Summarization percentages do not add up to 100.')

    # Compare simulation results with true steady-state probabilities
    diff = np.abs(np.array(freq) - pi_true * 100)
    if np.any(diff > tolerance):
        print(f'Some of your results are out of the acceptable range.')
        print(f'Higher range: {list(pi_true * 100 + tolerance)}')
        print(f'Your result: {freq}')
        print(f'Lower range: {list(pi_true * 100 - tolerance)}')
        return False
    else:
        print(f'Results are in the acceptable range.')
        print(f'Higher range: {list(pi_true * 100 + tolerance)}')
        print(f'Your result: {freq}')
        print(f'Lower range: {list(pi_true * 100 - tolerance)}')
        return True

# Transitions without 'snowy'
transitions = {
    'sunny': {'sunny': 0.7, 'cloudy': 0.3, 'rainy': 0.0},
    'cloudy': {'sunny': 0.5, 'cloudy': 0.3, 'rainy': 0.2},
    'rainy': {'sunny': 0.6, 'cloudy': 0.2, 'rainy': 0.2}
}

wrong_transitions = {
    'sunny': {'sunny': 0.7, 'cloudy': 0.3, 'rainy': 0.1},  # Sum > 1
    'cloudy': {'sunny': 0.5, 'cloudy': 0.3, 'rainy': 0.2},
    'rainy': {'sunny': 0.6, 'cloudy': 0.2, 'rainy': 0.2}
}

holding_time = {'sunny': 1, 'cloudy': 2, 'rainy': 2}

states = list(transitions.keys())

# Calculate embedded steady-state probabilities for the transition matrix
transition_matrix = np.array([
    [transitions['sunny']['sunny'], transitions['sunny']['cloudy'], transitions['sunny']['rainy']],
    [transitions['cloudy']['sunny'], transitions['cloudy']['cloudy'], transitions['cloudy']['rainy']],
    [transitions['rainy']['sunny'], transitions['rainy']['cloudy'], transitions['rainy']['rainy']]
])

pi_embed = calculate_embedded_steady_state(transition_matrix)

# Calculate true steady-state probabilities considering holding times
pi_true = calculate_true_steady_state(pi_embed, holding_time)

# Define tolerance levels
tolerance = 5.0  # Allow ±5% deviation

# Output the calculated steady-state probabilities
print(f"\nCalculated steady-state probabilities (expected long-term distribution):")
for i, state in enumerate(states):
    print(f"{state}: {pi_true[i] * 100:.2f}%")

# Run formal tests
check_formalities(transitions, holding_time)

if not check_exception(wrong_transitions, holding_time):
    print("Exception handling did not work as instructed.")
    sys.exit('NOK!')

if not check_holding_times(transitions, holding_time):
    print("Probably a problem with holding times")
    sys.exit('NOK!')
else:
    print("Correct holding times")

# Run the simulation test and check results
if run_test(transitions, holding_time, pi_true, tolerance):
    print("\nAll tests passed")
    sys.exit('OK!')
else:
    sys.exit('NOK!')






