# app.py

from flask import Flask, request, jsonify, render_template
from assignment_code import WeatherSimulation
import numpy as np

app = Flask(__name__)

# Initialize WeatherSimulation with default parameters
default_transitions = {
    'sunny': {'sunny': 0.7, 'cloudy': 0.3, 'rainy': 0.0},
    'cloudy': {'sunny': 0.5, 'cloudy': 0.3, 'rainy': 0.2},
    'rainy': {'sunny': 0.6, 'cloudy': 0.2, 'rainy': 0.2}
}

default_holding_times = {'sunny': 1, 'cloudy': 2, 'rainy': 2}

weather_sim = WeatherSimulation(default_transitions, default_holding_times)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    hours = data.get('hours', 10000)
    
    # Optional: Update transition probabilities and holding times if provided
    transitions = data.get('transitions')
    holding_times = data.get('holding_times')
    
    global weather_sim
    try:
        if transitions and holding_times:
            weather_sim = WeatherSimulation(transitions, holding_times)
        result = weather_sim.simulate(hours)
        states = weather_sim.get_states()
        return jsonify({'status': 'success', 'states': states, 'frequencies': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_states', methods=['GET'])
def get_states():
    states = weather_sim.get_states()
    return jsonify({'states': states})

if __name__ == '__main__':
    app.run(debug=True)



