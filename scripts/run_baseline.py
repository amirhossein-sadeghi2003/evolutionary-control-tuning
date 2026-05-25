from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pid_controller import PIDController
from src.ball_beam_sim import BallBeamConfig, simulate_controller, calculate_metrics


def beam_point(position, angle, length):
    local_x = position - length / 2
    x = local_x * np.cos(angle)
    y = local_x * np.sin(angle)
    return x, y


def save_response_plot(result, metrics, output_path):
    time = result["time"]
    position = result["position"]
    angle = np.rad2deg(result["angle"])
    target = result["target"]

    fig, ax1 = plt.subplots(figsize=(8, 4))

    ax1.plot(time, position, label="ball position")
    ax1.axhline(target, linestyle="--", label="target")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Position on beam (m)")
    ax1.set_ylim(-0.05, 1.05)

    ax2 = ax1.twinx()
    ax2.plot(time, angle, linestyle=":", label="beam angle")
    ax2.set_ylabel("Beam angle (degree)")

    title = "Manual PID baseline"
    if metrics["settling_time"] is not None:
        title += f" | settling time: {metrics['settling_time']:.2f}s"
    fig.suptitle(title)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_animation(result, metrics, output_path):
    time = result["time"]
    position = result["position"]
    angle = result["angle"]
    target = result["target"]
    length = result["length"]

    frame_step = 4
    frames = range(0, len(time), frame_step)

    fig = plt.figure(figsize=(9, 4.5))
    grid = fig.add_gridspec(1, 2, width_ratios=[3.2, 1.1])

    ax = fig.add_subplot(grid[0, 0])
    info_ax = fig.add_subplot(grid[0, 1])

    fig.suptitle("Manual PID baseline: simplified ball-and-beam control", fontsize=13)

    ax.set_xlim(-0.65, 0.65)
    ax.set_ylim(-0.35, 0.35)
    ax.set_aspect("equal")
    ax.set_xlabel("Beam x-axis")
    ax.set_ylabel("Beam y-axis")
    ax.grid(True, alpha=0.25)

    info_ax.axis("off")
    info_ax.set_title("Live state", fontsize=11, loc="left")

    beam_line, = ax.plot([], [], linewidth=5)
    ball = plt.Circle((0, 0), 0.035)
    target_marker, = ax.plot([], [], marker="x", markersize=12)
    text = info_ax.text(0.0, 0.90, "", fontsize=10, va="top", family="monospace")

    ax.add_patch(ball)

    def init():
        beam_line.set_data([], [])
        target_marker.set_data([], [])
        ball.center = (0, 0)
        text.set_text("")
        return beam_line, ball, target_marker, text

    def update(frame_index):
        theta = angle[frame_index]

        left_x, left_y = beam_point(0.0, theta, length)
        right_x, right_y = beam_point(length, theta, length)

        ball_x, ball_y = beam_point(position[frame_index], theta, length)
        target_x, target_y = beam_point(target, theta, length)

        beam_line.set_data([left_x, right_x], [left_y, right_y])
        ball.center = (ball_x, ball_y + 0.04)
        target_marker.set_data([target_x], [target_y + 0.08])

        text.set_text(
            f"time:\n"
            f"{time[frame_index]:.2f} s\n\n"
            f"position:\n"
            f"{position[frame_index]:.3f} m\n\n"
            f"target:\n"
            f"{target:.3f} m\n\n"
            f"beam angle:\n"
            f"{np.rad2deg(theta):.2f} deg\n\n"
            f"mean error:\n"
            f"{metrics['mean_error']:.3f}"
        )

        return beam_line, ball, target_marker, text

    animation = FuncAnimation(
        fig,
        update,
        frames=frames,
        init_func=init,
        interval=40,
        blit=True,
    )

    fig.tight_layout()
    animation.save(output_path, writer=PillowWriter(fps=25))
    plt.close(fig)


def main():
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    config = BallBeamConfig()

    controller = PIDController(
        kp=2.0,
        ki=0.0,
        kd=0.2,
        output_limit=config.max_angle_rad,
    )

    result = simulate_controller(controller, config)
    metrics = calculate_metrics(result)

    save_response_plot(
        result,
        metrics,
        results_dir / "baseline_response.png",
    )

    save_animation(
        result,
        metrics,
        results_dir / "baseline_ball_beam.gif",
    )

    print("Baseline simulation finished.")
    print(f"mean_error: {metrics['mean_error']:.4f}")
    print(f"final_error: {metrics['final_error']:.4f}")
    print(f"max_error: {metrics['max_error']:.4f}")
    print(f"overshoot: {metrics['overshoot']:.4f}")
    print(f"settling_time: {metrics['settling_time']}")
    print("Saved:")
    print("results/baseline_response.png")
    print("results/baseline_ball_beam.gif")


if __name__ == "__main__":
    main()
