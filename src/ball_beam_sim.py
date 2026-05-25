from dataclasses import dataclass
import numpy as np


@dataclass
class BallBeamConfig:
    length: float = 1.0
    target: float = 0.70
    start_position: float = 0.15
    start_velocity: float = 0.0
    dt: float = 0.02
    duration: float = 8.0
    gravity: float = 9.81
    damping: float = 0.30
    max_angle_rad: float = np.deg2rad(12)


def simulate_controller(controller, config=None):
    if config is None:
        config = BallBeamConfig()

    steps = int(config.duration / config.dt)

    position = config.start_position
    velocity = config.start_velocity

    time_log = []
    position_log = []
    velocity_log = []
    angle_log = []
    error_log = []

    controller.reset()

    for i in range(steps):
        t = i * config.dt

        error = config.target - position
        angle = controller.update(error, config.dt)

        acceleration = config.gravity * np.sin(angle) - config.damping * velocity

        velocity += acceleration * config.dt
        position += velocity * config.dt

        if position < 0:
            position = 0
            velocity = abs(velocity) * 0.2

        if position > config.length:
            position = config.length
            velocity = -abs(velocity) * 0.2

        time_log.append(t)
        position_log.append(position)
        velocity_log.append(velocity)
        angle_log.append(angle)
        error_log.append(error)

    return {
        "time": np.array(time_log),
        "position": np.array(position_log),
        "velocity": np.array(velocity_log),
        "angle": np.array(angle_log),
        "error": np.array(error_log),
        "target": config.target,
        "length": config.length,
    }


def calculate_metrics(result, tolerance=0.03):
    time = result["time"]
    position = result["position"]
    target = result["target"]

    error = np.abs(position - target)

    mean_error = float(np.mean(error))
    final_error = float(error[-1])
    max_error = float(np.max(error))

    overshoot = float(max(0.0, np.max(position - target)))

    settling_time = None
    for i in range(len(error)):
        if np.all(error[i:] < tolerance):
            settling_time = float(time[i])
            break

    return {
        "mean_error": mean_error,
        "final_error": final_error,
        "max_error": max_error,
        "overshoot": overshoot,
        "settling_time": settling_time,
    }
