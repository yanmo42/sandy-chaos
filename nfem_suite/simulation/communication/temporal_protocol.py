"""
Temporal Protocol Module
========================
Encodes/decodes temporal packets used to align cross-frame communication.
"""

from dataclasses import dataclass
from typing import Dict, Any
import hashlib


@dataclass
class TemporalPacket:
    payload: Any
    tau_send: complex
    sigma_send: int
    confidence: float = 1.0
    checksum: str = ""

    def compute_checksum(self) -> str:
        digest = hashlib.sha256(str(self.payload).encode("utf-8")).hexdigest()
        self.checksum = digest
        return digest


class TemporalProtocol:
    """Minimal packet encoder/decoder with alignment error estimation."""

    def encode(self, payload: Any, tau_send: complex, sigma_send: int, confidence: float = 1.0) -> TemporalPacket:
        packet = TemporalPacket(payload=payload, tau_send=tau_send, sigma_send=sigma_send, confidence=confidence)
        packet.compute_checksum()
        return packet

    def decode(self, packet: TemporalPacket, tau_recv: complex, tau_expected: complex) -> Dict[str, Any]:
        checksum_ok = packet.checksum == hashlib.sha256(str(packet.payload).encode("utf-8")).hexdigest()
        alignment_error = abs((tau_recv - packet.tau_send) - tau_expected)
        return {
            "payload": packet.payload,
            "checksum_ok": checksum_ok,
            "alignment_error": float(alignment_error),
            "tau_recv": tau_recv,
            "tau_send": packet.tau_send,
            "sigma_send": packet.sigma_send,
            "confidence": packet.confidence,
        }