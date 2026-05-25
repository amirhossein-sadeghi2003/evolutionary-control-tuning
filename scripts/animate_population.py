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


def make_candidates(config):
    raw_candidates = [
        {"name": "C1", "kp": 0.8, "ki": 0.0, "kd": 0.0},
        {"name": "C2", "kp": 1.2, "ki": 0.0, "kd": 0.1},
        {"name": "C3", "kp": 1.8, "ki": 0.0, "kd": 0.2},
        {"name": "C4", "kp": 2.4, "ki": 0.05, "kd": 0.3},
        {"name": "C5", "kp": 3.0, "ki": 0.02, "kd": 0.6},
        {"name": "C6", "kp": 4.0, "ki": 0.10, "kd": 0.8},
    ]

    candidates = []

    for item in raw_candidates:
        controller = PIDController(
            kp=item["kp"],
            ki=item["ki"],
            kd=item["kd"],
            output_limit=config.max_angle_rad,
        )
        result = simulate_controller(controller, config)
        metrics = calculate_metrics(result)

        candidates.append(
            {
                "name": item["name"],
                "kp": item["kp"],
                "ki": item["ki"],
                "kd": item["kd"],
                "result": result,
                "metrics": metrics,
            }
        )

    return candidates


def save_population_animation(candidates, output_path):
    frame_step = 4
    frames = range(0, len(candidates[0]["result"]["time"]), frame_step)

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    fig.suptitle("Population preview: multiple PID controllers on the ball-and-beam system", fontsize=14)

    artists = []

    for ax, candidate in zip(axes.flat, candidates):
        result = candidate["result"]
        length = result["length"]
        target = result["target"]

        ax.set_xlim(-0.65, 0.65)
        ax.set_ylim(-0.35, 0.35)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)
        ax.set_xticks([])
        ax.set_yticks([])

        beam_line, = ax.plot([], [], linewidth=4)
        target_marker, = ax.plot([], [], marker="x", markersize=10)
        ball = plt.Circle((0, 0), 0.03)
        ax.add_patch(ball)

        title = (
            f"{candidate['name']} | "
            f"Kp={candidate['kp']:.2f}, "
            f"Ki={candidate['ki']:.2f}, "
            f"Kd={candidate['kd']:.2f}"
        )
        ax.set_title(title, fontsize=10)

        info_text = ax.text(
            0.02,
            0.95,
            "",
            transform=ax.transAxes,
            va="top",
            fontsize=8,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        artists.append(
            {
                "ax": ax,
                "beam_line": beam_line,
                "target_marker": target_marker,
                "ball": ball,
                "text": info_text,
                "result": result,
                "metrics": candidate["metrics"],
                "target": target,
                "length": length,
            }
        )

    def init():
        updated = []
        for item in artists:
            item["beam_line"].set_data([], [])
            item["target_marker"].set_data([], [])
            item["ball"].center = (0, 0)
            item["text"].set_text("")
            updated.extend([item["beam_line"], item["target_marker"], item["ball"], item["text"]])
        return updated

    def update(frame_index):
        updated = []

        for item in artists:
            result = item["result"]
            theta = result["angle"][frame_index]
            position = result["position"][frame_index]
            target = item["target"]
            length = item["length"]

            left_x, left_y = beam_point(0.0, theta, length)
            right_x, right_y = beam_point(length, theta, length)

            ball_x, ball_y = beam_point(position, theta, length)
            target_x, target_y = beam_point(target, theta, length)

            item["beam_line"].set_data([left_x, right_x], [left_y, right_y])
            item["target_marker"].set_data([target_x], [target_y + 0.07])
            item["ball"].center = (ball_x, ball_y + 0.035)

            settling = item["metrics"]["settling_time"]
            if settling is None:
                settling_text = "None"
            else:
                settling_text = f"{settling:.2f}s"

            item["text"].set_text(
                f"t={result['time'][frame_index]:.2f}s\n"
                f"pos={position:.3f}m\n"
                f"err={abs(position - target):.3f}\n"
                f"mean={item['metrics']['mean_error']:.3f}\n"
                f"over={item['metrics']['overshoot']:.3f}\n"
                f"set={settling_text}"
            )

            updated.extend([item["beam_line"], item["target_marker"], item["ball"], item["text"]])

        return updated

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
    candidates = make_candidates(config)

    save_population_animation(
        candidates,
        results_dir / "population_preview.gif",
    )

    print("Population preview finished.")
    for item in candidates:
        metrics = item["metrics"]
        print(
            f"{item['name']} -> "
            f"Kp={item['kp']}, Ki={item['ki']}, Kd={item['kd']} | "
            f"mean_error={metrics['mean_error']:.4f}, "
            f"overshoot={metrics['overshoot']:.4f}, "
            f"settling_time={metrics['settling_time']}"
        )
    print("Saved:")
    print("results/population_preview.gif")


if __name__ == "__main__":
    main()
