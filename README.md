# Evolutionary Control Tuning

A visual simulation project for tuning controllers with evolutionary optimization.

## Project idea

This project uses a Genetic Algorithm to tune PID controller gains for a simplified ball-and-beam control system.

Each candidate controller is represented as:

Kp, Ki, Kd

The controller is evaluated by how well it can move and stabilize a ball near a target position. Poor controllers may overshoot, oscillate, or fail to stabilize the system. Better controllers should reach the target faster and remain more stable.

## Why this project

This project connects three areas:

- control systems
- optimization
- intelligent physical systems

The goal is not only to find good PID gains, but also to visualize how the optimization process improves controllers over generations.

## Planned visual outputs

- population evolution animation
- best controller progress animation
- baseline PID vs evolved PID comparison
- fitness curve over generations
- final controller metrics

## Planned structure

src/
- ball_beam_sim.py
- pid_controller.py
- genetic_algorithm.py
- fitness.py
- visualize.py

scripts/
- run_baseline.py
- run_evolution.py
- animate_population.py
- compare_best_controller.py

results/
- generated plots and animations

## Current status

Initial project structure.

## First visual baseline

The first implemented step is a simplified ball-and-beam simulation with a manually selected PID controller.

Generated outputs:

- `results/baseline_response.png`
- `results/baseline_ball_beam.gif`

This baseline is intentionally simple. It gives a reference controller before adding the Genetic Algorithm optimizer.

## Population preview

To make the optimization process more visual, the project now includes a population preview animation.

Generated output:

- `results/population_preview.gif`

This animation shows multiple PID controllers acting on the same simplified ball-and-beam system. It gives an early visual intuition for how different controller parameters produce different behaviors before adding the full Genetic Algorithm.

## Genetic Algorithm optimizer

The project now includes a Genetic Algorithm for tuning PID gains.

Each individual in the population contains three values:

- `Kp`
- `Ki`
- `Kd`

The optimizer evaluates each controller on the simplified ball-and-beam system and assigns a fitness score based on tracking error, final error, overshoot, settling behavior, and control effort.

Generated outputs:

- `results/ga_history.csv`
- `results/final_metrics.csv`
- `results/fitness_curve.png`
- `results/best_controller_response.png`

Lower fitness is better.

## Baseline vs evolved controller

The project also compares the manually selected baseline PID controller with the GA-tuned controller.

Generated outputs:

- `results/controller_comparison.csv`
- `results/baseline_vs_evolved_response.png`
- `results/baseline_vs_evolved.gif`

This comparison makes the effect of evolutionary tuning easier to see: both controllers are tested on the same simplified ball-and-beam system, and their tracking behavior is visualized side by side.
