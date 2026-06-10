"""Convert a StarCraft II keylog CSV into tempo_point_v0 JSONL.

Reads a keylog CSV captured by an AutoHotkey logger and emits windowed
``tempo_point/v0`` records (see schemas/tempo_point_v0.schema.json). Input keys
are classified into categorical classes and counted only -- the verbatim key
column is NEVER written to output, per redaction-policy-v0.

Usage::

    python scripts/sc2_keylog_to_tempo_points.py <keylog.csv> \
        [--window-ms 10000] [--out-dir memory/research/tempo]

Dependencies: stdlib + jsonschema (for the validation pass).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "tempo_point/v0"
REDACTION_VERSION = "redaction-policy-v0"
SOURCE = "game:sc2"

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "tempo_point_v0.schema.json"

# --- key vocabularies (used only to classify; keys are never echoed) ---------

MODIFIER_KEYS = {
    "Shift", "Ctrl", "Alt",
    "LShift", "RShift", "LCtrl", "RCtrl", "LAlt", "RAlt",
    "Control", "Menu",
}
MOVEMENT_KEYS = {"Up", "Down", "Left", "Right", "WheelUp", "WheelDown"}
NUMBER_KEYS = {str(d) for d in range(0, 10)}
MOUSE_PRIMARY_KEYS = {"LButton", "MButton"}
MOUSE_SECONDARY_KEYS = {"RButton"}


def classify_key(key: str) -> str | None:
    """Map a raw key name to a categorical class. Never returns the key."""
    if not key:
        return None
    if key in MOUSE_PRIMARY_KEYS:
        return "mouse_primary"
    if key in MOUSE_SECONDARY_KEYS:
        return "mouse_secondary"
    if key in MODIFIER_KEYS:
        return "modifier"
    if key in MOVEMENT_KEYS:
        return "movement"
    if key in NUMBER_KEYS:
        return "hotkey"
    if len(key) >= 2 and key[0] in {"F", "f"} and key[1:].isdigit():
        return "hotkey"  # F1-F12 camera/function keys
    if len(key) == 1 and key.isalpha():
        return "hotkey"  # ability / build hotkeys
    return None


def _is_letter(key: str) -> bool:
    return len(key) == 1 and key.isalpha()


def _is_function_key(key: str) -> bool:
    return len(key) >= 2 and key[0] in {"F", "f"} and key[1:].isdigit()


def session_id_for(path: Path) -> str:
    """Derive an opaque 16-char alphanumeric session id from the filename."""
    digest = hashlib.sha256(path.name.encode("utf-8")).hexdigest()
    return digest[:16]


# --- parsing -----------------------------------------------------------------

def parse_rows(csv_path: Path) -> list[dict]:
    """Parse the keylog CSV into normalized event dicts, sorted by time."""
    events: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                unix_ms = int(row["unix_ms"])
            except (KeyError, TypeError, ValueError):
                continue
            key = (row.get("key") or "").strip()
            events.append({
                "unix_ms": unix_ms,
                "key": key,
                "shift": (row.get("shift") or "0").strip() == "1",
                "ctrl": (row.get("ctrl") or "0").strip() == "1",
                "alt": (row.get("alt") or "0").strip() == "1",
                "key_class": classify_key(key),
                "is_letter": _is_letter(key),
                "is_function": _is_function_key(key),
                "is_number": key in NUMBER_KEYS,
            })
    events.sort(key=lambda e: e["unix_ms"])
    return events


# --- aggregation -------------------------------------------------------------

def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    rank = pct / 100.0 * (len(sorted_vals) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = rank - lo
    return float(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac)


def modal_key_class(events: list[dict]) -> str:
    counts: dict[str, int] = {}
    for e in events:
        cls = e["key_class"]
        if cls is not None:
            counts[cls] = counts.get(cls, 0) + 1
    if not counts:
        return "none"
    total = sum(counts.values())
    top_cls, top_n = max(counts.items(), key=lambda kv: kv[1])
    if len(counts) == 1:
        return top_cls
    if top_n / total >= 0.60:
        return top_cls
    return "mixed"


def compute_metrics(events: list[dict], window_ms: int) -> dict:
    n = len(events)
    window_s = window_ms / 1000.0
    key_events = [e for e in events if e["key_class"] not in ("mouse_primary", "mouse_secondary")]
    click_events = [e for e in events if e["key_class"] in ("mouse_primary", "mouse_secondary")]
    number_events = [e for e in events if e["is_number"]]
    movement_events = [e for e in events if e["key_class"] == "movement"]
    modifier_events = [e for e in events if e["key_class"] == "modifier"]
    hotkey_events = [e for e in events if e["key_class"] == "hotkey"]
    function_events = [e for e in events if e["is_function"]]

    key_count = len(key_events)
    click_count = len(click_events)

    apm = n / window_s * 60.0 if window_s > 0 else 0.0
    click_rate_hz = click_count / window_s if window_s > 0 else 0.0

    non_mouse_fraction = key_count / n if n else 0.0
    number_fraction = len(number_events) / n if n else 0.0
    camera_fraction = (len(movement_events) + len(function_events)) / n if n else 0.0

    intervals = []
    ms = sorted(e["unix_ms"] for e in events)
    for a, b in zip(ms, ms[1:]):
        intervals.append(float(b - a))
    intervals_sorted = sorted(intervals)

    return {
        "event_count": n,
        "key_count": key_count,
        "click_count": click_count,
        "number_count": len(number_events),
        "movement_count": len(movement_events),
        "modifier_count": len(modifier_events),
        "hotkey_count": len(hotkey_events),
        "function_count": len(function_events),
        "apm": apm,
        "click_rate_hz": click_rate_hz,
        "non_mouse_fraction": non_mouse_fraction,
        "number_fraction": number_fraction,
        "camera_fraction": camera_fraction,
        "intervals": intervals,
        "intervals_sorted": intervals_sorted,
        "modal_key_class": modal_key_class(events),
    }


def classify_action(m: dict) -> str:
    """Classify a window into a modal action class from its metrics."""
    if m["event_count"] == 0:
        return "none"
    if m["apm"] < 20:
        return "idle"
    if m["number_fraction"] > 0.30:
        return "control_group"
    if m["apm"] > 200 and m["click_rate_hz"] > 3:
        return "engagement"
    if m["click_rate_hz"] > 3 and m["movement_count"] > 0:
        return "micro"
    if m["non_mouse_fraction"] > 0.60 and m["click_rate_hz"] < 1.0:
        hk_mod = m["hotkey_count"] + m["modifier_count"]
        if m["apm"] <= 120 and hk_mod / m["event_count"] > 0.5:
            return "build_order"
        return "macro"
    if m["camera_fraction"] > 0.5 and m["click_rate_hz"] < 1.0:
        return "camera"
    return "mixed"


def detect_decision(events: list[dict], m: dict, rolling_avg_apm: float) -> tuple[bool, str, int]:
    """Detect whether a window contains a decision event.

    Returns (is_decision, decision_flag_kind, decision_count).
    """
    count = 0
    kinds: list[str] = []

    # APM spike vs. rolling session average.
    apm_spike = rolling_avg_apm > 0 and m["apm"] > 1.5 * rolling_avg_apm
    if apm_spike:
        count += 1
        kinds.append("engagement_initiated" if m["click_rate_hz"] > 3 else "other")

    # Build/tech hotkey burst: modifier held + letter key.
    mod_letter = sum(1 for e in events if e["is_letter"] and (e["shift"] or e["ctrl"] or e["alt"]))
    if mod_letter >= 2:
        count += 1
        kinds.append("build_order_change")

    # Control-group reassignment: Ctrl + number key.
    ctrl_num = sum(1 for e in events if e["is_number"] and e["ctrl"])
    if ctrl_num >= 1:
        count += 1
        kinds.append("other")

    if count == 0:
        return False, "", 0

    # Priority for the reported kind.
    priority = [
        "engagement_initiated",
        "build_order_change",
        "tech_switch",
        "expansion",
        "scout_dispatch",
        "engagement_disengaged",
        "other",
    ]
    kind = next((k for k in priority if k in kinds), "other")
    return True, kind, count


# --- record assembly ---------------------------------------------------------

def _ts_iso(unix_ms: int) -> str:
    return datetime.fromtimestamp(unix_ms / 1000.0, tz=timezone.utc).isoformat()


def _interval_aggs(m: dict) -> dict:
    intervals = m["intervals"]
    if not intervals:
        return {}
    s = m["intervals_sorted"]
    return {
        "inter_event_interval_ms_mean": round(sum(intervals) / len(intervals), 3),
        "inter_event_interval_ms_p50": round(_percentile(s, 50), 3),
        "inter_event_interval_ms_p95": round(_percentile(s, 95), 3),
        "inter_event_interval_ms_max": round(max(intervals), 3),
    }


def build_records(events: list[dict], session_id: str, window_ms: int) -> tuple[list[dict], int]:
    """Build tempo_point records over tumbling windows. Returns (records, n_windows)."""
    records: list[dict] = []
    if not events:
        return records, 0

    start = events[0]["unix_ms"]
    windows: dict[int, list[dict]] = {}
    for e in events:
        widx = (e["unix_ms"] - start) // window_ms
        windows.setdefault(widx, []).append(e)

    window_s = window_ms / 1000.0
    rolling_sum = 0.0
    rolling_n = 0
    n_windows = 0

    for widx in sorted(windows):
        win = windows[widx]
        n_windows += 1
        window_end_ms = start + (widx + 1) * window_ms
        ts = _ts_iso(window_end_ms)
        m = compute_metrics(win, window_ms)

        rolling_avg = rolling_sum / rolling_n if rolling_n else 0.0

        # apm_window point (always emitted for non-empty windows).
        aggregates = {
            "event_count": m["event_count"],
            "key_count": m["key_count"],
            "click_count": m["click_count"],
            "apm": round(m["apm"], 3),
            "click_rate_hz": round(m["click_rate_hz"], 3),
            "modal_key_class": m["modal_key_class"],
            "modal_action_class": classify_action(m),
        }
        aggregates.update(_interval_aggs(m))
        records.append({
            "schema_version": SCHEMA_VERSION,
            "ts": ts,
            "session_id": session_id,
            "source": SOURCE,
            "window_ms": window_ms,
            "point_kind": "apm_window",
            "aggregates": aggregates,
            "redaction_version": REDACTION_VERSION,
        })

        # decision_flag point (only when a decision is detected).
        is_decision, kind, decision_count = detect_decision(win, m, rolling_avg)
        if is_decision:
            decision_rate = decision_count / window_s if window_s > 0 else 0.0
            records.append({
                "schema_version": SCHEMA_VERSION,
                "ts": ts,
                "session_id": session_id,
                "source": SOURCE,
                "window_ms": window_ms,
                "point_kind": "decision_flag",
                "aggregates": {
                    "event_count": m["event_count"],
                    "decision_count": decision_count,
                    "decision_rate_hz": round(decision_rate, 3),
                    "apm": round(m["apm"], 3),
                    "modal_key_class": m["modal_key_class"],
                    "modal_action_class": classify_action(m),
                    "decision_flag_kind": kind,
                },
                "redaction_version": REDACTION_VERSION,
            })

        # Update rolling average AFTER using it for spike detection.
        rolling_sum += m["apm"]
        rolling_n += 1

    return records, n_windows


# --- validation --------------------------------------------------------------

def validate_records(records: list[dict]) -> list[str]:
    """Validate every record against the schema. Returns a list of error strings."""
    try:
        import jsonschema
    except ImportError:
        return ["__no_jsonschema__"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for i, rec in enumerate(records):
        for err in validator.iter_errors(rec):
            errors.append(f"record {i} ({rec.get('point_kind')}): {err.message}")
    return errors


# --- main --------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert SC2 keylog CSV to tempo_point_v0 JSONL.")
    parser.add_argument("csv_path", type=Path, help="Path to the keylog CSV.")
    parser.add_argument("--window-ms", type=int, default=10000, help="Tumbling window size in ms (default 10000).")
    parser.add_argument("--out-dir", type=Path, default=Path("memory/research/tempo"),
                        help="Base output directory (default memory/research/tempo).")
    args = parser.parse_args(argv)

    if not args.csv_path.is_file():
        print(f"error: input not found: {args.csv_path}", file=sys.stderr)
        return 2
    if args.window_ms < 1 or args.window_ms > 600000:
        print(f"error: --window-ms must be in [1, 600000], got {args.window_ms}", file=sys.stderr)
        return 2

    events = parse_rows(args.csv_path)
    session_id = session_id_for(args.csv_path)
    records, n_windows = build_records(events, session_id, args.window_ms)

    out_dir = args.out_dir / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.csv_path.stem}.jsonl"
    with out_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")

    errors = validate_records(records)
    no_validator = errors == ["__no_jsonschema__"]

    print(f"input:           {args.csv_path}")
    print(f"session_id:      {session_id}")
    print(f"events parsed:   {len(events)}")
    print(f"windows:         {n_windows}")
    print(f"tempo points:    {len(records)}")
    print(f"output:          {out_path}")
    if no_validator:
        print("validation:      SKIPPED (jsonschema not installed)")
        return 0
    if errors:
        print(f"validation:      FAILED ({len(errors)} error(s))")
        for e in errors[:20]:
            print(f"  - {e}")
        return 1
    print(f"validation:      OK ({len(records)} records valid)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
