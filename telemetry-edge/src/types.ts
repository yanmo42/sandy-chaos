// TypeScript mirror of schemas/tempo_point_v0.schema.json.
// The schema is canonical; these types exist for compile-time safety inside the edge.
// Any change here MUST be made in lockstep with the JSON schema, or the schema test will fail.

export type TempoPointSource =
  | "game:sc2"
  | "game:arc-raiders"
  | "game:fortnite"
  | "game:league"
  | "game:cyberpunk"
  | "game:other"
  | "input:keyboard"
  | "input:mouse"
  | "mixed";

export type PointKind =
  | "apm_window"
  | "interval_cluster"
  | "decision_flag"
  | "game_state_delta";

export type KeyClass =
  | "movement"
  | "hotkey"
  | "modifier"
  | "mouse_primary"
  | "mouse_secondary"
  | "mixed"
  | "none";

export type ActionClass =
  | "macro"
  | "micro"
  | "control_group"
  | "camera"
  | "build_order"
  | "engagement"
  | "retreat"
  | "idle"
  | "mixed"
  | "none";

export type Phase = "opening" | "early" | "mid" | "late" | "endgame" | "unknown";

export type DecisionFlagKind =
  | "build_order_change"
  | "engagement_initiated"
  | "engagement_disengaged"
  | "expansion"
  | "tech_switch"
  | "scout_dispatch"
  | "other";

export interface GameStateAggregates {
  unit_count_delta?: number;
  supply_delta?: number;
  resource_delta_primary?: number;
  resource_delta_secondary?: number;
  score_delta?: number;
  phase?: Phase;
  engagement_flag?: boolean;
}

export interface TempoAggregates {
  event_count?: number;
  key_count?: number;
  click_count?: number;
  decision_count?: number;
  apm?: number;
  click_rate_hz?: number;
  decision_rate_hz?: number;
  inter_event_interval_ms_mean?: number;
  inter_event_interval_ms_p50?: number;
  inter_event_interval_ms_p95?: number;
  inter_event_interval_ms_max?: number;
  modal_key_class?: KeyClass;
  modal_action_class?: ActionClass;
  game_state?: GameStateAggregates;
  decision_flag_kind?: DecisionFlagKind;
}

export interface TempoPoint {
  schema_version: "tempo_point/v0";
  ts: string;
  session_id: string;
  source: TempoPointSource;
  window_ms: number;
  point_kind: PointKind;
  aggregates: TempoAggregates;
  redaction_version: "redaction-policy-v0";
  notes?: string;
}

// Raw input event types. These NEVER appear in tempo_point output.
// They exist only inside the edge process, in the ring buffer, never serialized.

export type RawKeyClassTag = KeyClass;
export type RawActionClassTag = ActionClass;

export interface RawKeyEvent {
  kind: "key";
  ts: number; // monotonic ms since session start
  key_class: RawKeyClassTag; // categorical class, NOT the literal key
  action_class?: RawActionClassTag;
}

export interface RawMouseEvent {
  kind: "mouse";
  ts: number;
  button: "primary" | "secondary";
  action_class?: RawActionClassTag;
}

export interface RawDecisionEvent {
  kind: "decision";
  ts: number;
  decision_flag_kind: DecisionFlagKind;
}

export interface RawGameStateDelta {
  kind: "game_state";
  ts: number;
  delta: GameStateAggregates;
}

export type RawEvent =
  | RawKeyEvent
  | RawMouseEvent
  | RawDecisionEvent
  | RawGameStateDelta;
