"""
Emergency Vehicle Detection & Green Corridor System
Detects ambulances, fire trucks, and police vehicles.
Automatically clears and holds a green corridor along their route.
"""

import time
import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import threading


class EmergencyVehicleType(Enum):
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE = "police_car"
    UNKNOWN = "unknown"


class CorridorStatus(Enum):
    INACTIVE = "INACTIVE"
    ACTIVATING = "ACTIVATING"
    ACTIVE = "ACTIVE"
    CLEARING = "CLEARING"
    CLEARED = "CLEARED"


@dataclass
class EmergencyEvent:
    event_id: str
    vehicle_type: EmergencyVehicleType
    detected_lane: int
    detected_at: float
    confidence: float
    corridor_activated: bool = False
    corridor_activation_time: Optional[float] = None
    corridor_cleared_time: Optional[float] = None
    total_corridor_duration: float = 0.0
    vehicles_held: int = 0


@dataclass
class CorridorState:
    status: CorridorStatus
    active_lane: Optional[int]
    blocked_lanes: list
    event: Optional[EmergencyEvent]
    activation_time: Optional[float]
    estimated_clear_time: Optional[float]
    alert_message: str = ""


class EmergencyDetector:
    """
    Monitors detection results for emergency vehicles.
    Uses confirmation logic to prevent false positives.
    """

    EMERGENCY_KEYWORDS = ["ambulance", "fire_truck", "police", "fire truck", "police car"]
    CONFIRMATION_FRAMES = 2   # Require detection in N consecutive frames

    def __init__(self):
        self._detection_buffer = []     # Recent frame detections
        self._confirmed_events = []     # Confirmed emergency events
        self._event_counter = 0

    def process_frame_result(self, frame_result) -> Optional[EmergencyEvent]:
        """
        Process a FrameDetectionResult and return a confirmed EmergencyEvent if detected.
        Returns None if no confirmed emergency.
        """
        has_emergency = frame_result.emergency_detected
        self._detection_buffer.append(has_emergency)

        # Keep only recent frames
        if len(self._detection_buffer) > 10:
            self._detection_buffer.pop(0)

        # Check if we have confirmation
        recent = self._detection_buffer[-self.CONFIRMATION_FRAMES:]
        confirmed = len(recent) >= self.CONFIRMATION_FRAMES and all(recent)

        if confirmed and frame_result.emergency_vehicles:
            ev = frame_result.emergency_vehicles[0]
            self._event_counter += 1
            event = EmergencyEvent(
                event_id=f"EMG-{self._event_counter:04d}",
                vehicle_type=self._classify(ev.class_name),
                detected_lane=ev.lane_id or 0,
                detected_at=time.time(),
                confidence=ev.confidence,
            )
            return event

        return None

    def _classify(self, class_name: str) -> EmergencyVehicleType:
        name = class_name.lower()
        if "ambulance" in name:
            return EmergencyVehicleType.AMBULANCE
        elif "fire" in name:
            return EmergencyVehicleType.FIRE_TRUCK
        elif "police" in name:
            return EmergencyVehicleType.POLICE
        return EmergencyVehicleType.UNKNOWN


class GreenCorridorController:
    """
    Manages the AI-powered green corridor.
    Coordinates with TrafficOptimizationEngine to clear routes.
    """

    # How long to maintain corridor after vehicle passes (seconds)
    CORRIDOR_HOLD_DURATION = 20.0
    CORRIDOR_ACTIVATION_DELAY = 1.5   # Activation propagation time

    def __init__(self, num_lanes: int = 4):
        self.num_lanes = num_lanes
        self._lock = threading.Lock()
        self.status = CorridorStatus.INACTIVE
        self.active_event: Optional[EmergencyEvent] = None
        self.active_lane: Optional[int] = None
        self.activation_time: Optional[float] = None
        self.hold_until: Optional[float] = None
        self._event_history: list = []
        self._alert_log: list = []

    def activate(self, event: EmergencyEvent, engine) -> CorridorState:
        """
        Activate green corridor for the emergency event.
        Immediately commands the traffic engine to hold target lane green.
        """
        with self._lock:
            if self.status in (CorridorStatus.ACTIVE, CorridorStatus.ACTIVATING):
                # Update if same corridor, otherwise log conflict
                if self.active_lane != event.detected_lane:
                    self._log_alert(f"⚠️  Corridor conflict: already active on lane {self.active_lane}")
                return self._get_state()

            self.status = CorridorStatus.ACTIVATING
            self.active_event = event
            self.active_lane = event.detected_lane
            self.activation_time = time.time()

            alert = (
                f"🚨 EMERGENCY CORRIDOR ACTIVATED\n"
                f"Vehicle: {event.vehicle_type.value.upper()}\n"
                f"Lane: {event.detected_lane + 1}\n"
                f"Confidence: {event.confidence:.0%}\n"
                f"Event ID: {event.event_id}"
            )
            self._log_alert(alert)
            print(f"[GreenCorridor] {alert}")

            # Command engine
            engine.trigger_emergency(event.detected_lane)
            event.corridor_activated = True
            event.corridor_activation_time = time.time()

            self.status = CorridorStatus.ACTIVE
            self.hold_until = time.time() + self.CORRIDOR_HOLD_DURATION

        return self._get_state()

    def check_and_clear(self, engine) -> bool:
        """
        Check if corridor should be cleared. Returns True if cleared.
        """
        with self._lock:
            if self.status != CorridorStatus.ACTIVE:
                return False

            if time.time() >= self.hold_until:
                self._clear(engine)
                return True

        return False

    def manual_clear(self, engine):
        """Manually clear the emergency corridor."""
        with self._lock:
            if self.status == CorridorStatus.ACTIVE:
                self._clear(engine)

    def get_state(self) -> CorridorState:
        with self._lock:
            return self._get_state()

    def get_alert_log(self) -> list:
        with self._lock:
            return list(self._alert_log)

    def get_event_history(self) -> list:
        with self._lock:
            return list(self._event_history)

    def _clear(self, engine):
        """Internal: clear the corridor."""
        if self.active_event:
            self.active_event.corridor_cleared_time = time.time()
            self.active_event.total_corridor_duration = (
                self.active_event.corridor_cleared_time - self.active_event.corridor_activation_time
            )
            self._event_history.append(self.active_event)

        engine.clear_emergency()
        self.status = CorridorStatus.CLEARED
        self._log_alert(f"✅ Emergency corridor cleared after {self.CORRIDOR_HOLD_DURATION:.0f}s hold.")
        print("[GreenCorridor] Corridor cleared, resuming normal operation.")

        # Reset
        self.active_event = None
        self.active_lane = None
        self.activation_time = None
        self.hold_until = None
        self.status = CorridorStatus.INACTIVE

    def _get_state(self) -> CorridorState:
        blocked = [i for i in range(self.num_lanes) if i != self.active_lane]
        est_clear = None
        if self.hold_until:
            est_clear = max(0, self.hold_until - time.time())

        latest_alert = self._alert_log[-1] if self._alert_log else ""

        return CorridorState(
            status=self.status,
            active_lane=self.active_lane,
            blocked_lanes=blocked if self.status == CorridorStatus.ACTIVE else [],
            event=self.active_event,
            activation_time=self.activation_time,
            estimated_clear_time=est_clear,
            alert_message=latest_alert,
        )

    def _log_alert(self, message: str):
        entry = {"timestamp": time.time(), "message": message}
        self._alert_log.append(entry)
        if len(self._alert_log) > 100:
            self._alert_log.pop(0)
