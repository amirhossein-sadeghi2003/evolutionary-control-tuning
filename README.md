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
