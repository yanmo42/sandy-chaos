"""Toy simulation for a Rimuru-style adaptive substrate snap model.

The goal is to test whether an adaptive agent in a structured field can move
from reactive local adaptation to external coherence organization after crossing
an operational threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Agent:
    x: int
    y: int
    energy: float = 10.0
    capability_score: float = 0.0
    sensing_radius: int = 1
    control_radius: int = 0
    predictive_depth: int = 0
    snapped: bool = False
    snapped_at: int | None = None
    reactive_actions: int = 0
    organizing_actions: int = 0


@dataclass
class SimConfig:
    size: int = 32
    steps: int = 200
    seed: int = 7
    resource_scale: float = 1.0
    hazard_scale: float = 1.0
    disorder_scale: float = 1.0
    move_cost: float = 0.15
    stabilize_cost: float = 0.25
    snap_margin: float = 0.95
    rolling_window: int = 12


@dataclass
class SimResult:
    energy: list[float] = field(default_factory=list)
    capability: list[float] = field(default_factory=list)
    avg_cost: list[float] = field(default_factory=list)
    local_disorder: list[float] = field(default_factory=list)
    stabilized_cells: list[int] = field(default_factory=list)
    snapped_at: int | None = None


class RimuruSnapSim:
    def __init__(self, config: SimConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.resources = self.rng.random((config.size, config.size)) * config.resource_scale
        self.hazards = self.rng.random((config.size, config.size)) * config.hazard_scale
        self.disorder = self.rng.random((config.size, config.size)) * config.disorder_scale
        self.agent = Agent(x=config.size // 2, y=config.size // 2)
        self.cost_history: list[float] = []

    def neighborhood(self, x: int, y: int, radius: int):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx = np.clip(x + dx, 0, self.config.size - 1)
                ny = np.clip(y + dy, 0, self.config.size - 1)
                yield int(nx), int(ny)

    def local_disorder(self) -> float:
        vals = [self.disorder[nx, ny] for nx, ny in self.neighborhood(self.agent.x, self.agent.y, max(1, self.agent.control_radius))]
        return float(np.mean(vals))

    def best_move(self) -> tuple[int, int, float]:
        best = None
        for nx, ny in self.neighborhood(self.agent.x, self.agent.y, self.agent.sensing_radius):
            resource = self.resources[nx, ny]
            hazard = self.hazards[nx, ny] * max(0.2, 1.0 - 0.08 * self.agent.capability_score)
            disorder = self.disorder[nx, ny]
            score = resource - 0.7 * hazard - 0.3 * disorder
            if best is None or score > best[2]:
                best = (nx, ny, score)
        assert best is not None
        return best

    def absorb(self, x: int, y: int) -> None:
        gained = self.resources[x, y] * 0.35
        self.agent.capability_score += gained
        self.agent.energy += self.resources[x, y] * 0.2
        self.resources[x, y] *= 0.6

        self.agent.sensing_radius = min(4, 1 + int(self.agent.capability_score // 1.5))
        self.agent.predictive_depth = min(2, int(self.agent.capability_score // 2.5))
        self.agent.control_radius = min(3, int(self.agent.capability_score // 3.5))

    def maybe_snap(self, step: int) -> None:
        if self.agent.snapped:
            return
        if len(self.cost_history) < self.config.rolling_window:
            return

        reactive_cost = float(np.mean(self.cost_history[-self.config.rolling_window:]))
        local_disorder = self.local_disorder()
        stabilize_efficiency = self.config.stabilize_cost / (1.0 + self.agent.control_radius + self.agent.capability_score * 0.15)
        organizing_cost = stabilize_efficiency * max(0.1, local_disorder)

        if organizing_cost < reactive_cost * self.config.snap_margin and self.agent.control_radius >= 1:
            self.agent.snapped = True
            self.agent.snapped_at = step

    def stabilize(self) -> int:
        if self.agent.control_radius <= 0:
            return 0
        changed = 0
        for nx, ny in self.neighborhood(self.agent.x, self.agent.y, self.agent.control_radius):
            before = self.disorder[nx, ny]
            reduction = min(before, 0.08 + 0.02 * self.agent.capability_score)
            self.disorder[nx, ny] -= reduction
            self.hazards[nx, ny] *= 0.98
            if self.disorder[nx, ny] < before:
                changed += 1
        self.agent.energy -= self.config.stabilize_cost
        self.agent.organizing_actions += 1
        return changed

    def step(self, step: int) -> tuple[float, int]:
        nx, ny, _ = self.best_move()
        self.agent.x, self.agent.y = nx, ny

        cell_hazard = self.hazards[nx, ny] * max(0.2, 1.0 - 0.08 * self.agent.capability_score)
        movement_cost = self.config.move_cost + 0.4 * cell_hazard
        self.agent.energy -= movement_cost
        self.cost_history.append(movement_cost)
        self.agent.reactive_actions += 1

        self.absorb(nx, ny)
        self.maybe_snap(step)

        stabilized = 0
        if self.agent.snapped:
            stabilized = self.stabilize()

        self.agent.energy = max(self.agent.energy, 0.0)
        return movement_cost, stabilized

    def run(self) -> SimResult:
        result = SimResult()
        for step in range(self.config.steps):
            avg_cost, stabilized = self.step(step)
            result.energy.append(self.agent.energy)
            result.capability.append(self.agent.capability_score)
            result.avg_cost.append(avg_cost)
            result.local_disorder.append(self.local_disorder())
            result.stabilized_cells.append(stabilized)
            if self.agent.snapped and result.snapped_at is None:
                result.snapped_at = self.agent.snapped_at
            if self.agent.energy <= 0:
                break
        return result


def plot_result(result: SimResult, out_path: Path) -> None:
    steps = np.arange(len(result.energy))
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    axes[0].plot(steps, result.capability, label="capability score")
    axes[0].set_ylabel("capability")
    axes[0].legend(loc="upper left")

    axes[1].plot(steps, result.avg_cost, label="action cost", color="tab:red")
    axes[1].set_ylabel("cost")
    axes[1].legend(loc="upper left")

    axes[2].plot(steps, result.local_disorder, label="local disorder", color="tab:orange")
    axes[2].set_ylabel("disorder")
    axes[2].legend(loc="upper left")

    axes[3].plot(steps, result.stabilized_cells, label="stabilized cells", color="tab:green")
    axes[3].set_ylabel("organized")
    axes[3].set_xlabel("step")
    axes[3].legend(loc="upper left")

    if result.snapped_at is not None:
        for ax in axes:
            ax.axvline(result.snapped_at, linestyle="--", alpha=0.6, color="black")

    fig.suptitle("Rimuru-style adaptive substrate snap simulation")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    config = SimConfig()
    sim = RimuruSnapSim(config)
    result = sim.run()
    out = Path("docs/notes/rimuru_snap_sim_plot.png")
    plot_result(result, out)
    print(
        {
            "steps": len(result.energy),
            "snapped_at": result.snapped_at,
            "final_energy": round(result.energy[-1], 3),
            "final_capability": round(result.capability[-1], 3),
            "plot": str(out),
        }
    )


if __name__ == "__main__":
    main()
