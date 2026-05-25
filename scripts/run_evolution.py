from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ball_beam_sim import BallBeamConfig
from src.genetic_algorithm import GAConfig, run_genetic_algorithm


def save_history_csv(history, output_path):
    df = pd.DataFrame(history)
    df.to_csv(output_path, index=False)


def save_final_metrics(best_record, output_path):
    metrics = best_record["metrics"]

    data = {
        "kp": [best_record["kp"]],
        "ki": [best_record["ki"]],
        "kd": [best_record["kd"]],
        "fitness": [best_record["fitness"]],
        "mean_error": [metrics["mean_error"]],
        "final_error": [metrics["final_error"]],
        "max_error": [metrics["max_error"]],
        "overshoot": [metrics["overshoot"]],
        "settling_time": [metrics["settling_time"]],
    }

    pd.DataFrame(data).to_csv(output_path, index=False)


def save_fitness_curve(history, output_path):
    generations = [item["generation"] for item in history]
    best = [item["best_fitness"] for item in history]
    mean = [item["mean_fitness"] for item in history]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(generations, best, label="best fitness")
    ax.plot(generations, mean, label="mean fitness", linestyle="--")

    ax.set_title("Genetic Algorithm fitness over generations")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness score (lower is better)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_best_response(best_record, output_path):
    result = best_record["result"]
    time = result["time"]
    position = result["position"]
    target = result["target"]
    angle = np.rad2deg(result["angle"])

    fig, ax1 = plt.subplots(figsize=(8, 4))

    ax1.plot(time, position, label="ball position")
    ax1.axhline(target, linestyle="--", label="target")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Position on beam (m)")
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(time, angle, linestyle=":", label="beam angle")
    ax2.set_ylabel("Beam angle (degree)")

    title = (
        "Best GA-tuned PID response | "
        f"Kp={best_record['kp']:.3f}, "
        f"Ki={best_record['ki']:.3f}, "
        f"Kd={best_record['kd']:.3f}"
    )
    fig.suptitle(title)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main():
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    system_config = BallBeamConfig()
    ga_config = GAConfig()

    best_record, history = run_genetic_algorithm(system_config, ga_config)

    save_history_csv(history, results_dir / "ga_history.csv")
    save_final_metrics(best_record, results_dir / "final_metrics.csv")
    save_fitness_curve(history, results_dir / "fitness_curve.png")
    save_best_response(best_record, results_dir / "best_controller_response.png")

    metrics = best_record["metrics"]

    print("Genetic Algorithm finished.")
    print(f"best_kp: {best_record['kp']:.4f}")
    print(f"best_ki: {best_record['ki']:.4f}")
    print(f"best_kd: {best_record['kd']:.4f}")
    print(f"fitness: {best_record['fitness']:.4f}")
    print(f"mean_error: {metrics['mean_error']:.4f}")
    print(f"final_error: {metrics['final_error']:.4f}")
    print(f"overshoot: {metrics['overshoot']:.4f}")
    print(f"settling_time: {metrics['settling_time']}")
    print("Saved:")
    print("results/ga_history.csv")
    print("results/final_metrics.csv")
    print("results/fitness_curve.png")
    print("results/best_controller_response.png")


if __name__ == "__main__":
    main()
