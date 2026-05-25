from pathlib import Path
import sys
import numpy as np
import pandas as pd
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


def run_controller(kp, ki, kd, config):
    controller = PIDController(
        kp=kp,
        ki=ki,
        kd=kd,
        output_limit=config.max_angle_rad,
    )

    result = simulate_controller(controller, config)
    metrics = calculate_metrics(result)

    return result, metrics


def save_comparison_csv(baseline_metrics, evolved_metrics, evolved_gains, output_path):
    rows = [
        {
            "controller": "manual_baseline",
            "kp": 2.0,
            "ki": 0.0,
            "kd": 0.2,
            "mean_error": baseline_metrics["mean_error"],
            "final_error": baseline_metrics["final_error"],
            "max_error": baseline_metrics["max_error"],
            "overshoot": baseline_metrics["overshoot"],
            "settling_time": baseline_metrics["settling_time"],
        },
        {
            "controller": "ga_evolved",
            "kp": evolved_gains["kp"],
            "ki": evolved_gains["ki"],
            "kd": evolved_gains["kd"],
            "mean_error": evolved_metrics["mean_error"],
            "final_error": evolved_metrics["final_error"],
            "max_error": evolved_metrics["max_error"],
            "overshoot": evolved_metrics["overshoot"],
            "settling_time": evolved_metrics["settling_time"],
        },
    ]

    pd.DataFrame(rows).to_csv(output_path, index=False)


def save_response_comparison_plot(baseline_result, evolved_result, output_path):
    time = baseline_result["time"]
    target = baseline_result["target"]

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(time, baseline_result["position"], label="manual baseline")
    ax.plot(time, evolved_result["position"], label="GA evolved")
    ax.axhline(target, linestyle="--", label="target")

    ax.set_title("Manual PID vs GA-tuned PID")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ball position on beam (m)")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_side_by_side_animation(baseline_result, evolved_result, baseline_metrics, evolved_metrics, evolved_gains, output_path):
    frame_step = 4
    frames = range(0, len(baseline_result["time"]), frame_step)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.suptitle("Manual PID baseline vs GA-tuned PID controller", fontsize=14)

    controllers = [
        {
            "title": "Manual PID baseline",
            "result": baseline_result,
            "metrics": baseline_metrics,
            "kp": 2.0,
            "ki": 0.0,
            "kd": 0.2,
        },
        {
            "title": "GA-tuned PID",
            "result": evolved_result,
            "metrics": evolved_metrics,
            "kp": evolved_gains["kp"],
            "ki": evolved_gains["ki"],
            "kd": evolved_gains["kd"],
        },
    ]

    artists = []

    for ax, item in zip(axes, controllers):
        result = item["result"]

        ax.set_xlim(-0.65, 0.65)
        ax.set_ylim(-0.35, 0.35)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)
        ax.set_xticks([])
        ax.set_yticks([])

        title = (
            f"{item['title']}\n"
            f"Kp={item['kp']:.3f}, Ki={item['ki']:.3f}, Kd={item['kd']:.3f}"
        )
        ax.set_title(title, fontsize=10)

        beam_line, = ax.plot([], [], linewidth=5)
        target_marker, = ax.plot([], [], marker="x", markersize=12)
        ball = plt.Circle((0, 0), 0.035)
        ax.add_patch(ball)

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
                "beam_line": beam_line,
                "target_marker": target_marker,
                "ball": ball,
                "text": info_text,
                "result": result,
                "metrics": item["metrics"],
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

            time = result["time"][frame_index]
            position = result["position"][frame_index]
            angle = result["angle"][frame_index]
            target = result["target"]
            length = result["length"]

            left_x, left_y = beam_point(0.0, angle, length)
            right_x, right_y = beam_point(length, angle, length)

            ball_x, ball_y = beam_point(position, angle, length)
            target_x, target_y = beam_point(target, angle, length)

            item["beam_line"].set_data([left_x, right_x], [left_y, right_y])
            item["ball"].center = (ball_x, ball_y + 0.04)
            item["target_marker"].set_data([target_x], [target_y + 0.08])

            settling = item["metrics"]["settling_time"]
            if settling is None:
                settling_text = "None"
            else:
                settling_text = f"{settling:.2f}s"

            item["text"].set_text(
                f"t={time:.2f}s\n"
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

    config = BallBeamConfig()

    final_metrics_path = results_dir / "final_metrics.csv"
    final_metrics = pd.read_csv(final_metrics_path).iloc[0]

    evolved_gains = {
        "kp": float(final_metrics["kp"]),
        "ki": float(final_metrics["ki"]),
        "kd": float(final_metrics["kd"]),
    }

    baseline_result, baseline_metrics = run_controller(2.0, 0.0, 0.2, config)
    evolved_result, evolved_metrics = run_controller(
        evolved_gains["kp"],
        evolved_gains["ki"],
        evolved_gains["kd"],
        config,
    )

    save_comparison_csv(
        baseline_metrics,
        evolved_metrics,
        evolved_gains,
        results_dir / "controller_comparison.csv",
    )

    save_response_comparison_plot(
        baseline_result,
        evolved_result,
        results_dir / "baseline_vs_evolved_response.png",
    )

    save_side_by_side_animation(
        baseline_result,
        evolved_result,
        baseline_metrics,
        evolved_metrics,
        evolved_gains,
        results_dir / "baseline_vs_evolved.gif",
    )

    print("Controller comparison finished.")
    print("Manual baseline:")
    print(f"mean_error: {baseline_metrics['mean_error']:.4f}")
    print(f"overshoot: {baseline_metrics['overshoot']:.4f}")
    print(f"settling_time: {baseline_metrics['settling_time']}")
    print("GA evolved:")
    print(f"kp: {evolved_gains['kp']:.4f}")
    print(f"ki: {evolved_gains['ki']:.4f}")
    print(f"kd: {evolved_gains['kd']:.4f}")
    print(f"mean_error: {evolved_metrics['mean_error']:.4f}")
    print(f"overshoot: {evolved_metrics['overshoot']:.4f}")
    print(f"settling_time: {evolved_metrics['settling_time']}")
    print("Saved:")
    print("results/controller_comparison.csv")
    print("results/baseline_vs_evolved_response.png")
    print("results/baseline_vs_evolved.gif")


if __name__ == "__main__":
    main()
