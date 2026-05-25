from dataclasses import dataclass
import numpy as np

from src.fitness import evaluate_pid_gains


@dataclass
class GAConfig:
    population_size: int = 30
    generations: int = 35
    mutation_rate: float = 0.25
    mutation_scale: float = 0.18
    elite_count: int = 3
    seed: int = 7

    kp_range: tuple = (0.0, 6.0)
    ki_range: tuple = (0.0, 0.6)
    kd_range: tuple = (0.0, 1.5)


def _clip_individual(individual, ga_config):
    individual[0] = np.clip(individual[0], *ga_config.kp_range)
    individual[1] = np.clip(individual[1], *ga_config.ki_range)
    individual[2] = np.clip(individual[2], *ga_config.kd_range)
    return individual


def _random_population(rng, ga_config):
    population = np.zeros((ga_config.population_size, 3))

    population[:, 0] = rng.uniform(*ga_config.kp_range, size=ga_config.population_size)
    population[:, 1] = rng.uniform(*ga_config.ki_range, size=ga_config.population_size)
    population[:, 2] = rng.uniform(*ga_config.kd_range, size=ga_config.population_size)

    return population


def _tournament_select(rng, evaluated, tournament_size=3):
    indexes = rng.choice(len(evaluated), size=tournament_size, replace=False)
    best_index = min(indexes, key=lambda idx: evaluated[idx]["fitness"])
    return evaluated[best_index]["individual"].copy()


def _crossover(rng, parent_a, parent_b):
    alpha = rng.uniform(0.25, 0.75)
    child = alpha * parent_a + (1.0 - alpha) * parent_b
    return child


def _mutate(rng, individual, ga_config):
    if rng.random() > ga_config.mutation_rate:
        return individual

    ranges = np.array(
        [
            ga_config.kp_range[1] - ga_config.kp_range[0],
            ga_config.ki_range[1] - ga_config.ki_range[0],
            ga_config.kd_range[1] - ga_config.kd_range[0],
        ]
    )

    noise = rng.normal(0.0, ga_config.mutation_scale, size=3) * ranges
    individual = individual + noise
    return _clip_individual(individual, ga_config)


def run_genetic_algorithm(system_config, ga_config=None):
    if ga_config is None:
        ga_config = GAConfig()

    rng = np.random.default_rng(ga_config.seed)
    population = _random_population(rng, ga_config)

    history = []
    best_record = None

    for generation in range(ga_config.generations):
        evaluated = []

        for i, individual in enumerate(population):
            kp, ki, kd = individual
            fitness, result, metrics = evaluate_pid_gains(kp, ki, kd, system_config)

            record = {
                "generation": generation,
                "index": i,
                "individual": individual.copy(),
                "kp": float(kp),
                "ki": float(ki),
                "kd": float(kd),
                "fitness": float(fitness),
                "result": result,
                "metrics": metrics,
            }

            evaluated.append(record)

        evaluated.sort(key=lambda item: item["fitness"])

        generation_best = evaluated[0]
        if best_record is None or generation_best["fitness"] < best_record["fitness"]:
            best_record = generation_best.copy()

        fitness_values = [item["fitness"] for item in evaluated]

        history.append(
            {
                "generation": generation,
                "best_fitness": float(np.min(fitness_values)),
                "mean_fitness": float(np.mean(fitness_values)),
                "best_kp": generation_best["kp"],
                "best_ki": generation_best["ki"],
                "best_kd": generation_best["kd"],
                "best_mean_error": generation_best["metrics"]["mean_error"],
                "best_final_error": generation_best["metrics"]["final_error"],
                "best_overshoot": generation_best["metrics"]["overshoot"],
                "best_settling_time": generation_best["metrics"]["settling_time"],
            }
        )

        next_population = []

        for elite in evaluated[:ga_config.elite_count]:
            next_population.append(elite["individual"].copy())

        while len(next_population) < ga_config.population_size:
            parent_a = _tournament_select(rng, evaluated)
            parent_b = _tournament_select(rng, evaluated)

            child = _crossover(rng, parent_a, parent_b)
            child = _mutate(rng, child, ga_config)
            child = _clip_individual(child, ga_config)

            next_population.append(child)

        population = np.array(next_population)

    return best_record, history
