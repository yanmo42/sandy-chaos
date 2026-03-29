#!/usr/bin/env python3
"""Minimal frame-aware corridor simulation.

This is an intentionally small toy model for testing whether temporal
discipline around delayed remote guidance can outperform simpler baselines.
It does not model propulsion or field engineering.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Sequence


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class CorridorSpec:
    amplitude: float = 1.2
    frequency: float = 0.18
    half_width: float = 0.9
    reference_speed: float = 1.8

    def __post_init__(self) -> None:
        if self.frequency <= 0.0:
            raise ValueError("frequency must be positive")
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.reference_speed <= 0.0:
            raise ValueError("reference_speed must be positive")

    def centerline_y(self, x: float) -> float:
        return self.amplitude * math.sin(self.frequency * x)

    def slope_at(self, x: float) -> float:
        return self.amplitude * self.frequency * math.cos(self.frequency * x)

    def cross_track_error(self, x: float, y: float) -> float:
        return y - self.centerline_y(x)


@dataclass(frozen=True)
class SimulationConfig:
    dt: float = 0.1
    steps: int = 240
    propagation_delay_steps: int = 3
    clock_mismatch_s: float = 0.12
    validity_window_s: float = 0.55
    disturbance_bias: float = 0.08
    disturbance_amplitude: float = 0.22
    disturbance_frequency: float = 1.4
    accel_limit: float = 2.8
    min_forward_speed: float = 0.6
    max_forward_speed: float = 2.6
    local_kp: float = 1.6
    local_kd: float = 1.0
    remote_kp: float = 2.8
    remote_kd: float = 1.5
    speed_kp: float = 1.1
    remote_blend: float = 0.72
    remote_lookahead_s: float = 0.55
    initial_x: float = 0.0
    initial_y_offset: float = 0.45
    initial_vx: float = 1.5
    initial_vy: float = 0.0

    def __post_init__(self) -> None:
        if self.dt <= 0.0:
            raise ValueError("dt must be positive")
        if self.steps <= 0:
            raise ValueError("steps must be positive")
        if self.propagation_delay_steps < 0:
            raise ValueError("propagation_delay_steps must be non-negative")
        if self.validity_window_s < 0.0:
            raise ValueError("validity_window_s must be non-negative")
        if self.accel_limit <= 0.0:
            raise ValueError("accel_limit must be positive")
        if self.min_forward_speed <= 0.0:
            raise ValueError("min_forward_speed must be positive")
        if self.max_forward_speed <= self.min_forward_speed:
            raise ValueError("max_forward_speed must exceed min_forward_speed")
        if not 0.0 <= self.remote_blend <= 1.0:
            raise ValueError("remote_blend must be in [0, 1]")
        if self.remote_lookahead_s < 0.0:
            raise ValueError("remote_lookahead_s must be non-negative")

    @property
    def one_way_delay_s(self) -> float:
        return self.propagation_delay_steps * self.dt

    @property
    def round_trip_delay_s(self) -> float:
        return 2.0 * self.one_way_delay_s


@dataclass(frozen=True)
class VehicleState:
    x: float
    y: float
    vx: float
    vy: float


@dataclass(frozen=True)
class RemotePacket:
    ax_cmd: float
    ay_cmd: float
    remote_send_time_s: float
    valid_until_remote_s: float
    local_expiry_time_s: float
    receive_time_s: float
    predicted_age_s: float


@dataclass(frozen=True)
class ControllerSummary:
    controller_name: str
    gamma_corridor: float
    violation_rate: float
    control_effort: float
    avg_cross_track_error: float
    max_cross_track_error: float
    packets_sent: int
    packets_received: int
    packets_applied_valid: int
    packets_applied_stale: int
    packets_rejected_expired: int


@dataclass
class ControllerRun:
    summary: ControllerSummary
    cross_track_errors: List[float]
    controls: List[float]


def compute_gamma_corridor(cross_track_errors: Sequence[float], half_width: float) -> float:
    if half_width <= 0.0:
        raise ValueError("half_width must be positive")
    if not cross_track_errors:
        raise ValueError("cross_track_errors must be non-empty")

    normalized = [min(1.0, abs(err) / half_width) for err in cross_track_errors]
    return 1.0 - sum(normalized) / len(normalized)


def _local_control(state: VehicleState, corridor: CorridorSpec, config: SimulationConfig) -> tuple[float, float]:
    desired_y = corridor.centerline_y(state.x)
    desired_vy = corridor.slope_at(state.x) * corridor.reference_speed
    ax = config.speed_kp * (corridor.reference_speed - state.vx)
    ay = -config.local_kp * (state.y - desired_y) + config.local_kd * (desired_vy - state.vy)
    return ax, ay


def _remote_control(
    observed_state: VehicleState,
    corridor: CorridorSpec,
    config: SimulationConfig,
    *,
    frame_aware: bool,
    send_time_local_s: float,
) -> RemotePacket:
    predicted_age_s = config.round_trip_delay_s if frame_aware else 0.0
    est_x = observed_state.x + observed_state.vx * predicted_age_s
    est_y = observed_state.y + observed_state.vy * predicted_age_s
    est_vx = observed_state.vx
    est_vy = observed_state.vy

    x_target = est_x + config.remote_lookahead_s * corridor.reference_speed
    desired_y = corridor.centerline_y(x_target)
    desired_vy = corridor.slope_at(x_target) * corridor.reference_speed

    ax_cmd = config.speed_kp * (corridor.reference_speed - est_vx)
    ay_cmd = -config.remote_kp * (est_y - desired_y) + config.remote_kd * (desired_vy - est_vy)

    remote_send_time_s = send_time_local_s + config.clock_mismatch_s
    valid_until_remote_s = remote_send_time_s + config.validity_window_s
    local_expiry_time_s = valid_until_remote_s - config.clock_mismatch_s
    receive_time_s = send_time_local_s + config.one_way_delay_s

    return RemotePacket(
        ax_cmd=ax_cmd,
        ay_cmd=ay_cmd,
        remote_send_time_s=remote_send_time_s,
        valid_until_remote_s=valid_until_remote_s,
        local_expiry_time_s=local_expiry_time_s,
        receive_time_s=receive_time_s,
        predicted_age_s=predicted_age_s,
    )


def run_controller(
    controller_name: str,
    corridor: CorridorSpec,
    config: SimulationConfig,
) -> ControllerRun:
    valid_names = {"local_only", "delay_ignorant_remote", "frame_aware_corridor"}
    if controller_name not in valid_names:
        raise ValueError(f"unknown controller_name: {controller_name}")

    state = VehicleState(
        x=config.initial_x,
        y=corridor.centerline_y(config.initial_x) + config.initial_y_offset,
        vx=config.initial_vx,
        vy=config.initial_vy,
    )

    observation_queue: Dict[int, List[VehicleState]] = {}
    packet_queue: Dict[int, List[RemotePacket]] = {}
    active_packet: RemotePacket | None = None

    packets_sent = 0
    packets_received = 0
    packets_applied_valid = 0
    packets_applied_stale = 0
    packets_rejected_expired = 0
    active_packet_was_counted = False

    cross_track_errors: List[float] = []
    controls: List[float] = []

    for step in range(config.steps):
        t = step * config.dt
        arrival_step = step + config.propagation_delay_steps
        observation_queue.setdefault(arrival_step, []).append(state)

        for observed_state in observation_queue.pop(step, []):
            if controller_name == "local_only":
                continue

            packet = _remote_control(
                observed_state,
                corridor,
                config,
                frame_aware=(controller_name == "frame_aware_corridor"),
                send_time_local_s=t,
            )
            packets_sent += 1
            packet_step = step + config.propagation_delay_steps
            packet_queue.setdefault(packet_step, []).append(packet)

        for packet in packet_queue.pop(step, []):
            packets_received += 1
            if controller_name == "frame_aware_corridor" and t > packet.local_expiry_time_s + 1e-12:
                packets_rejected_expired += 1
                continue
            active_packet = packet
            active_packet_was_counted = False

        local_ax, local_ay = _local_control(state, corridor, config)
        ax_cmd = local_ax
        ay_cmd = local_ay

        if controller_name != "local_only" and active_packet is not None:
            packet_is_stale = t > active_packet.local_expiry_time_s + 1e-12

            if controller_name == "delay_ignorant_remote":
                ax_cmd = (1.0 - config.remote_blend) * local_ax + config.remote_blend * active_packet.ax_cmd
                ay_cmd = (1.0 - config.remote_blend) * local_ay + config.remote_blend * active_packet.ay_cmd
                if packet_is_stale:
                    packets_applied_stale += 1
                else:
                    packets_applied_valid += 1
            elif not packet_is_stale:
                ax_cmd = (1.0 - config.remote_blend) * local_ax + config.remote_blend * active_packet.ax_cmd
                ay_cmd = (1.0 - config.remote_blend) * local_ay + config.remote_blend * active_packet.ay_cmd
                if not active_packet_was_counted:
                    packets_applied_valid += 1
                    active_packet_was_counted = True
            else:
                active_packet = None
                active_packet_was_counted = False

        ax_cmd = _clamp(ax_cmd, -config.accel_limit, config.accel_limit)
        ay_cmd = _clamp(ay_cmd, -config.accel_limit, config.accel_limit)

        disturbance_ay = config.disturbance_bias + config.disturbance_amplitude * math.sin(
            config.disturbance_frequency * t
        )
        next_vx = _clamp(state.vx + ax_cmd * config.dt, config.min_forward_speed, config.max_forward_speed)
        next_vy = state.vy + (ay_cmd + disturbance_ay) * config.dt
        next_x = state.x + next_vx * config.dt
        next_y = state.y + next_vy * config.dt

        cross_track_errors.append(corridor.cross_track_error(next_x, next_y))
        controls.append(ax_cmd * ax_cmd + ay_cmd * ay_cmd)
        state = VehicleState(x=next_x, y=next_y, vx=next_vx, vy=next_vy)

    gamma_corridor = compute_gamma_corridor(cross_track_errors, corridor.half_width)
    violation_rate = sum(abs(err) > corridor.half_width for err in cross_track_errors) / len(cross_track_errors)
    avg_cross_track_error = sum(abs(err) for err in cross_track_errors) / len(cross_track_errors)
    max_cross_track_error = max(abs(err) for err in cross_track_errors)
    control_effort = sum(controls) / len(controls)

    summary = ControllerSummary(
        controller_name=controller_name,
        gamma_corridor=gamma_corridor,
        violation_rate=violation_rate,
        control_effort=control_effort,
        avg_cross_track_error=avg_cross_track_error,
        max_cross_track_error=max_cross_track_error,
        packets_sent=packets_sent,
        packets_received=packets_received,
        packets_applied_valid=packets_applied_valid,
        packets_applied_stale=packets_applied_stale,
        packets_rejected_expired=packets_rejected_expired,
    )
    return ControllerRun(summary=summary, cross_track_errors=cross_track_errors, controls=controls)


def run_all_baselines(corridor: CorridorSpec, config: SimulationConfig) -> Dict[str, ControllerSummary]:
    names = ["local_only", "delay_ignorant_remote", "frame_aware_corridor"]
    return {name: run_controller(name, corridor, config).summary for name in names}


def run_delay_sweep(
    corridor: CorridorSpec,
    base_config: SimulationConfig,
    *,
    max_delay_steps: int,
) -> List[Dict[str, float | int | str]]:
    if max_delay_steps < 0:
        raise ValueError("max_delay_steps must be non-negative")

    rows: List[Dict[str, float | int | str]] = []
    for delay_steps in range(max_delay_steps + 1):
        config = SimulationConfig(**{**asdict(base_config), "propagation_delay_steps": delay_steps})
        results = run_all_baselines(corridor, config)
        for name, summary in results.items():
            rows.append(
                {
                    "delay_steps": delay_steps,
                    "controller_name": name,
                    "gamma_corridor": summary.gamma_corridor,
                    "violation_rate": summary.violation_rate,
                    "control_effort": summary.control_effort,
                    "packets_applied_valid": summary.packets_applied_valid,
                    "packets_applied_stale": summary.packets_applied_stale,
                    "packets_rejected_expired": summary.packets_rejected_expired,
                }
            )
    return rows


def _write_rows_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError("rows must be non-empty")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_optional_plot(path: Path, rows: Sequence[Dict[str, float | int | str]]) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for plotting") from exc

    grouped: Dict[str, List[tuple[int, float]]] = {}
    for row in rows:
        grouped.setdefault(str(row["controller_name"]), []).append(
            (int(row["delay_steps"]), float(row["gamma_corridor"]))
        )

    fig, ax = plt.subplots(figsize=(7, 4.2), constrained_layout=True)
    for name, series in grouped.items():
        series = sorted(series)
        ax.plot([x for x, _ in series], [y for _, y in series], marker="o", label=name)
    ax.set_xlabel("Propagation Delay Steps")
    ax.set_ylabel("Gamma_corridor")
    ax.set_ylim(0.0, 1.02)
    ax.set_title("Frame-Aware Corridor Delay Sweep")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimal frame-aware corridor simulation.")
    parser.add_argument("--out-dir", default="memory/frame_aware_corridor")
    parser.add_argument("--stem", default="frame_aware_corridor_v0_1")
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--delay-steps", type=int, default=3)
    parser.add_argument("--clock-mismatch-s", type=float, default=0.12)
    parser.add_argument("--validity-window-s", type=float, default=0.55)
    parser.add_argument("--corridor-half-width", type=float, default=0.9)
    parser.add_argument("--delay-sweep-max", type=int, default=None)
    parser.add_argument("--plot", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    corridor = CorridorSpec(half_width=args.corridor_half_width)
    config = SimulationConfig(
        dt=args.dt,
        steps=args.steps,
        propagation_delay_steps=args.delay_steps,
        clock_mismatch_s=args.clock_mismatch_s,
        validity_window_s=args.validity_window_s,
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.delay_sweep_max is None:
        results = run_all_baselines(corridor, config)
        rows = [asdict(summary) for summary in results.values()]
        json_path = out_dir / f"{args.stem}.json"
        csv_path = out_dir / f"{args.stem}.csv"
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "corridor": asdict(corridor),
                    "config": asdict(config),
                    "results": rows,
                },
                handle,
                indent=2,
            )
        _write_rows_csv(csv_path, rows)
        print(json.dumps({"json": str(json_path), "csv": str(csv_path)}, indent=2))
        return

    rows = run_delay_sweep(corridor, config, max_delay_steps=args.delay_sweep_max)
    json_path = out_dir / f"{args.stem}_sweep.json"
    csv_path = out_dir / f"{args.stem}_sweep.csv"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "corridor": asdict(corridor),
                "base_config": asdict(config),
                "delay_sweep_max": args.delay_sweep_max,
                "rows": rows,
            },
            handle,
            indent=2,
        )
    _write_rows_csv(csv_path, rows)

    plot_path = None
    if args.plot:
        plot_path = out_dir / f"{args.stem}_sweep.png"
        _write_optional_plot(plot_path, rows)

    print(json.dumps({"json": str(json_path), "csv": str(csv_path), "plot": str(plot_path) if plot_path else None}, indent=2))


if __name__ == "__main__":
    main()
