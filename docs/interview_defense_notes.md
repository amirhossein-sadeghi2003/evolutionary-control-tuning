# Interview Defense Notes

## Project goal

This project demonstrates how evolutionary optimization can be used to tune PID controller gains for a simplified physical control system.

The case study is a simplified ball-and-beam system. The goal is to move the ball toward a target position and keep it stable with less overshoot and lower tracking error.

## Why this project matters

The project connects:

- control systems
- physical system simulation
- PID tuning
- Genetic Algorithm optimization
- visual explanation of controller behavior

It fits the broader intelligent physical systems portfolio because it shows how optimization can improve controller behavior in a simulated physical system.

## Main idea

A PID controller is represented by three gains:

- Kp
- Ki
- Kd

The Genetic Algorithm searches for a better combination of these gains.

Each candidate controller is tested in the same ball-and-beam simulation. Its performance is converted into a fitness score. Lower fitness means better behavior.

## Main files

### `src/ball_beam_sim.py`

Defines the simplified ball-and-beam simulation.

It simulates:

- ball position
- ball velocity
- beam angle
- target position
- system response over time

The model is intentionally simple. It is not a full physics-accurate ball-and-beam model, but it is useful for visualizing controller tuning behavior.

### `src/pid_controller.py`

Implements the PID controller.

It calculates the control output from:

- proportional error
- integral error
- derivative error

The output is limited by the maximum allowed beam angle.

### `src/fitness.py`

Evaluates a candidate PID controller.

The fitness function penalizes:

- mean tracking error
- final error
- overshoot
- long settling time
- excessive control effort

This makes the controller search more realistic than optimizing only one metric.

### `src/genetic_algorithm.py`

Implements the Genetic Algorithm.

It includes:

- random population initialization
- tournament selection
- crossover
- mutation
- elitism

Each individual is a possible PID controller.

### `scripts/run_baseline.py`

Runs the manually selected baseline PID controller and generates:

- baseline response plot
- baseline ball-and-beam animation

### `scripts/animate_population.py`

Shows multiple candidate PID controllers acting on the same system.

This helps visualize why some controllers are unstable or slower than others.

### `scripts/run_evolution.py`

Runs the Genetic Algorithm and saves:

- best controller metrics
- fitness history
- best evolved response

### `scripts/compare_controllers.py`

Compares the manual baseline controller with the GA-tuned controller.

It generates a side-by-side animation and a metrics comparison table.

## Main results

The GA-tuned controller improved the baseline behavior.

Compared with the manual PID baseline, the evolved controller achieved:

- lower mean tracking error
- lower overshoot
- faster settling behavior

The visual comparison makes the improvement easier to understand than metrics alone.

## What the animations show

### Baseline animation

Shows how the manually selected PID controller moves the ball toward the target.

### Population preview

Shows several PID controllers at the same time, making it easier to see how different gains create different behavior.

### Baseline vs evolved animation

Shows the manual PID and GA-tuned PID side by side on the same task.

This is the strongest visual output because it directly shows the benefit of evolutionary tuning.

## Important limitation

The best evolved gains reached the upper edge of the selected search range.

This means the current search space or fitness function may need refinement. It does not make the project invalid, but it shows that the optimizer is pushing toward stronger gains within the allowed range.

A useful future improvement would be to:

- expand or redesign the PID gain search ranges
- add stronger penalties for aggressive control effort
- compare GA tuning with manual tuning, grid search, or Bayesian optimization
- use a more physically accurate ball-and-beam model

## How I would explain this project in an interview

I built a visual simulation to show how a Genetic Algorithm can tune PID gains for a simplified control problem. I first created a baseline PID controller, then visualized several different controllers, then implemented the GA optimizer, and finally compared the evolved controller with the manual baseline.

The main point of the project is not only the final PID gains. The point is to show the full tuning process visually: unstable or weaker controllers appear in the population, the GA selects better candidates, and the final controller is compared against the baseline.

## What I learned

This project helped me understand:

- how PID gains affect control behavior
- how to define a fitness function for controller tuning
- why optimization results depend strongly on search ranges and penalties
- how visualizations can make control and optimization easier to interpret
- why honest limitations are important in engineering documentation
