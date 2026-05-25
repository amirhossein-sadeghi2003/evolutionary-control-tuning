import numpy as np

from src.pid_controller import PIDController
from src.ball_beam_sim import simulate_controller, calculate_metrics


def evaluate_pid_gains(kp, ki, kd, config):
    controller = PIDController(
        kp=kp,
        ki=ki,
        kd=kd,
        output_limit=config.max_angle_rad,
    )

    result = simulate_controller(controller, config)
    metrics = calculate_metrics(result)

    error = np.abs(result["position"] - result["target"])
    angle = np.abs(result["angle"])

    mean_error = metrics["mean_error"]
    final_error = metrics["final_error"]
    overshoot = metrics["overshoot"]
    control_effort = float(np.mean(angle))

    if metrics["settling_time"] is None:
        settling_penalty = config.duration
    else:
        settling_penalty = metrics["settling_time"]

    fitness = (
        8.0 * mean_error
        + 5.0 * final_error
        + 2.5 * overshoot
        + 0.25 * settling_penalty
        + 0.5 * control_effort
    )

    return fitness, result, metrics
