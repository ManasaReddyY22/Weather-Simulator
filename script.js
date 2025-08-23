// static/script.js

document.addEventListener('DOMContentLoaded', function() {
    const transitionsContainer = document.getElementById('transitions-container');
    const holdingTimesContainer = document.getElementById('holding-times-container');
    const simulationForm = document.getElementById('simulation-form');
    const resultsDiv = document.getElementById('results');

    // Fetch states from the backend
    fetch('/get_states')
        .then(response => response.json())
        .then(data => {
            const states = data.states;
            generateTransitionInputs(states);
            generateHoldingTimeInputs(states);
        })
        .catch(error => {
            console.error('Error fetching states:', error);
            resultsDiv.innerHTML = `<p class="error">Error fetching states from the server.</p>`;
        });

    // Generate transition probability inputs
    function generateTransitionInputs(states) {
        states.forEach(fromState => {
            const fromDiv = document.createElement('div');
            fromDiv.classList.add('transition-group');
            const header = document.createElement('h4');
            header.textContent = `From "${fromState}" to:`;
            fromDiv.appendChild(header);

            states.forEach(toState => {
                const label = document.createElement('label');
                label.textContent = `P(${fromState} → ${toState}):`;
                label.setAttribute('for', `trans_${fromState}_${toState}`);

                const input = document.createElement('input');
                input.type = 'number';
                input.step = '0.01';
                input.min = '0';
                input.max = '1';
                input.id = `trans_${fromState}_${toState}`;
                input.name = `trans_${fromState}_${toState}`;
                input.value = '0.25'; // Default value

                fromDiv.appendChild(label);
                fromDiv.appendChild(input);
            });

            transitionsContainer.appendChild(fromDiv);
        });
    }

    // Generate holding time inputs
    function generateHoldingTimeInputs(states) {
        states.forEach(state => {
            const label = document.createElement('label');
            label.textContent = `Holding time for "${state}" (hours):`;
            label.setAttribute('for', `hold_${state}`);

            const input = document.createElement('input');
            input.type = 'number';
            input.step = '1';
            input.min = '1';
            input.id = `hold_${state}`;
            input.name = `hold_${state}`;
            input.value = '1'; // Default value

            holdingTimesContainer.appendChild(label);
            holdingTimesContainer.appendChild(input);
        });
    }

    // Handle form submission
    simulationForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(simulationForm);
        const hours = parseInt(formData.get('hours'));
        if (isNaN(hours) || hours < 1) {
            resultsDiv.innerHTML = `<p class="error">Please enter a valid number of hours.</p>`;
            return;
        }

        // Gather transition probabilities
        const transitions = {};
        const stateHeaders = Array.from(document.querySelectorAll('#transitions-container .transition-group h4'));
        const states = stateHeaders.map(h4 => {
            const match = h4.textContent.match(/From "(.*)" to:/);
            return match ? match[1] : null;
        }).filter(state => state !== null);

        states.forEach(fromState => {
            transitions[fromState] = {};
            states.forEach(toState => {
                const input = document.getElementById(`trans_${fromState}_${toState}`);
                const value = parseFloat(input.value);
                transitions[fromState][toState] = isNaN(value) ? 0 : value;
            });

            // Normalize probabilities to sum to 1
            const total = Object.values(transitions[fromState]).reduce((a, b) => a + b, 0);
            if (total === 0) {
                // Avoid division by zero by setting self-transition to 1
                transitions[fromState][fromState] = 1.0;
            } else {
                Object.keys(transitions[fromState]).forEach(toState => {
                    transitions[fromState][toState] /= total;
                });
            }
        });

        // Gather holding times
        const holding_times = {};
        states.forEach(state => {
            const input = document.getElementById(`hold_${state}`);
            const value = parseInt(input.value);
            holding_times[state] = isNaN(value) || value < 1 ? 1 : value;
        });

        // Prepare payload
        const payload = {
            hours: hours,
            transitions: transitions,
            holding_times: holding_times
        };

        // Send simulation request to backend
        fetch('/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayResults(data.states, data.frequencies);
            } else {
                resultsDiv.innerHTML = `<p class="error">Error: ${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Error running simulation:', error);
            resultsDiv.innerHTML = `<p class="error">An error occurred while running the simulation.</p>`;
        });
    });

    // Get weather icon based on state
    function getWeatherIcon(weather) {
        switch (weather) {
            case 'sunny': return '☀️';
            case 'cloudy': return '☁️';
            case 'rainy': return '🌧️';
            default: return '❓';
        }
    }

    // Display simulation results
    function displayResults(states, frequencies) {
        resultsDiv.innerHTML = '';
        states.forEach((state, index) => {
            const p = document.createElement('p');
            p.classList.add('result-item');
            p.textContent = `${getWeatherIcon(state)} ${state.charAt(0).toUpperCase() + state.slice(1)}: ${frequencies[index].toFixed(2)}%`;
            resultsDiv.appendChild(p);
        });
    }
});


