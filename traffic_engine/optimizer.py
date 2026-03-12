"""
Traffic Optimization Engine
Dynamically adjusts signal timings based on real-time traffic density.
Uses a weighted scoring system with fairness guarantees to prevent starvation.
"""

import time
import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import threading


class SignalState(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    EMERGENCY_HOLD = "EMERGENCY_HOLD"


class SignalPhase(Enum):
    NORMAL = "NORMAL"
    EMERGENCY_CORRIDOR = "EMERGENCY_CORRIDOR"
    TRANSITION = "TRANSITION"


@dataclass
class SignalTiming:
    green_duration: float   # seconds
    yellow_duration: float  # seconds
    red_duration: float     # seconds
    min_green: float = 8.0
    max_green: float = 60.0


@dataclass
class IntersectionSignal:
    lane_id: int
    state: SignalState = SignalState.RED
    remaining_seconds: float = 0.0
    current_timing: Optional[SignalTiming] = None
    phase: SignalPhase = SignalPhase.NORMAL
    cycles_since_green: int = 0
    total_wait_time: float = 0.0
    last_green_timestamp: float = 0.0
    vehicles_served: int = 0


@dataclass 
class OptimizationResult:
    lane_id: int
    recommended_green: float
    density_score: float
    fairness_bonus: float
    emergency_override: bool
    reasoning: str


@dataclass
class IntersectionState:
    signals: list           # List[IntersectionSignal]
    active_green_lane: int
    phase: SignalPhase
    cycle_number: int
    emergency_active: bool
    emergency_lane_id: Optional[int]
    total_vehicles_served: int
    avg_wait_time: float
    timestamp: float = field(default_factory=time.time)


class SignalTimingCalculator:
    """
    Calculates optimal green signal durations using density-weighted algorithm.

    Algorithm:
    1. Base time from vehicle count thresholds
    2. Weighted density multiplier applied
    3. Fairness bonus for lanes waiting too long
    4. Hard clamped to [min_green, max_green]
    """

    # Base timing table: (max_weighted_density) -> base_green_seconds
    TIMING_TABLE = [
        (5.0,   10),
        (15.0,  20),
        (30.0,  35),
        (50.0,  45),
        (float("inf"), 60),
    ]

    YELLOW_DURATION = 3.0
    MIN_GREEN = 8.0
    MAX_GREEN = 60.0
    MAX_WAIT_CYCLES = 3    # After this many cycles without green, apply fairness boost
    FAIRNESS_BONUS = 8.0   # Extra seconds added per over-waited cycle

    @classmethod
    def calculate(cls, density: float, cycles_since_green: int = 0) -> SignalTiming:
        """Compute timing given density score and starvation counter."""
        base_green = cls._base_green(density)

        # Fairness: prevent indefinite starvation
        starvation_bonus = 0.0
        if cycles_since_green >= cls.MAX_WAIT_CYCLES:
            extra = cycles_since_green - cls.MAX_WAIT_CYCLES + 1
            starvation_bonus = cls.FAIRNESS_BONUS * extra

        green = min(cls.MAX_GREEN, max(cls.MIN_GREEN, base_green + starvation_bonus))
        red_estimate = 30.0  # will be set dynamically by controller

        return SignalTiming(
            green_duration=round(green, 1),
            yellow_duration=cls.YELLOW_DURATION,
            red_duration=red_estimate,
            min_green=cls.MIN_GREEN,
            max_green=cls.MAX_GREEN,
        )

    @classmethod
    def _base_green(cls, density: float) -> float:
        for threshold, base in cls.TIMING_TABLE:
            if density <= threshold:
                return float(base)
        return float(cls.TIMING_TABLE[-1][1])

    @classmethod
    def explain(cls, density: float, cycles_since_green: int) -> str:
        base = cls._base_green(density)
        starvation = max(0, (cycles_since_green - cls.MAX_WAIT_CYCLES + 1)) * cls.FAIRNESS_BONUS
        return (
            f"Density={density:.1f} → base={base:.0f}s"
            + (f" + starvation_bonus={starvation:.0f}s" if starvation > 0 else "")
        )


class TrafficOptimizationEngine:
    """
    Core engine that manages intersection signal state and optimization.
    Runs asynchronously via internal timer loop.
    """

    def __init__(self, num_lanes: int = 4):
        self.num_lanes = num_lanes
        self._lock = threading.Lock()
        self._running = False

        self.signals = [
            IntersectionSignal(lane_id=i, state=SignalState.RED)
            for i in range(num_lanes)
        ]

        self.active_green_lane = 0
        self.phase = SignalPhase.NORMAL
        self.cycle_number = 0
        self.emergency_active = False
        self.emergency_lane_id: Optional[int] = None
        self.total_vehicles_served = 0

        self._current_densities = [0.0] * num_lanes
        self._current_green_remaining = 0.0
        self._current_yellow_remaining = 0.0
        self._in_yellow = False

        # Start with lane 0 green
        self._start_green(lane_id=0, density=5.0)

        # Background tick thread
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()
        self._running = True

    def update_densities(self, densities: list):
        """Called each frame with new lane density values."""
        with self._lock:
            self._current_densities = list(densities[:self.num_lanes])

    def trigger_emergency(self, lane_id: int):
        """Activate green corridor for specified lane."""
        with self._lock:
            if not self.emergency_active:
                print(f"[Engine] 🚨 EMERGENCY CORRIDOR activated for lane {lane_id}")
                self.emergency_active = True
                self.emergency_lane_id = lane_id
                self.phase = SignalPhase.EMERGENCY_CORRIDOR
                self._force_green(lane_id)

    def clear_emergency(self):
        """Deactivate emergency corridor."""
        with self._lock:
            if self.emergency_active:
                print("[Engine] ✅ Emergency corridor cleared")
                self.emergency_active = False
                self.emergency_lane_id = None
                self.phase = SignalPhase.NORMAL

    def get_state(self) -> IntersectionState:
        """Return current intersection state snapshot."""
        with self._lock:
            signals_copy = []
            for s in self.signals:
                remaining = 0.0
                if s.lane_id == self.active_green_lane:
                    remaining = self._current_green_remaining if not self._in_yellow else self._current_yellow_remaining
                signals_copy.append(IntersectionSignal(
                    lane_id=s.lane_id,
                    state=s.state,
                    remaining_seconds=round(remaining, 1),
                    phase=self.phase if s.state == SignalState.GREEN else SignalPhase.NORMAL,
                    cycles_since_green=s.cycles_since_green,
                    total_wait_time=s.total_wait_time,
                    last_green_timestamp=s.last_green_timestamp,
                    vehicles_served=s.vehicles_served,
                ))

            avg_wait = sum(s.total_wait_time for s in self.signals) / max(1, self.num_lanes)

            return IntersectionState(
                signals=signals_copy,
                active_green_lane=self.active_green_lane,
                phase=self.phase,
                cycle_number=self.cycle_number,
                emergency_active=self.emergency_active,
                emergency_lane_id=self.emergency_lane_id,
                total_vehicles_served=self.total_vehicles_served,
                avg_wait_time=round(avg_wait, 1),
                timestamp=time.time(),
            )

    def get_optimization_results(self) -> list:
        """Return current optimization decisions for all lanes."""
        with self._lock:
            results = []
            for i, density in enumerate(self._current_densities):
                timing = SignalTimingCalculator.calculate(density, self.signals[i].cycles_since_green)
                reasoning = SignalTimingCalculator.explain(density, self.signals[i].cycles_since_green)
                results.append(OptimizationResult(
                    lane_id=i,
                    recommended_green=timing.green_duration,
                    density_score=density,
                    fairness_bonus=max(0, (self.signals[i].cycles_since_green - SignalTimingCalculator.MAX_WAIT_CYCLES + 1)) * SignalTimingCalculator.FAIRNESS_BONUS,
                    emergency_override=(self.emergency_active and self.emergency_lane_id == i),
                    reasoning=reasoning,
                ))
            return results

    def _tick_loop(self):
        """Background loop that ticks signal timers every 0.5 seconds."""
        while True:
            time.sleep(0.5)
            with self._lock:
                self._tick(0.5)

    def _tick(self, dt: float):
        """Advance signal timers by dt seconds."""
        if self.emergency_active:
            # Keep emergency lane green indefinitely
            return

        if self._in_yellow:
            self._current_yellow_remaining -= dt
            if self._current_yellow_remaining <= 0:
                self._in_yellow = False
                self._advance_to_next_lane()
        else:
            self._current_green_remaining -= dt
            if self._current_green_remaining <= 0:
                # Start yellow phase
                self._in_yellow = True
                self._current_yellow_remaining = SignalTimingCalculator.YELLOW_DURATION
                self.signals[self.active_green_lane].state = SignalState.YELLOW

    def _advance_to_next_lane(self):
        """Select next lane to give green based on density optimization."""
        # Mark current green lane as red
        self.signals[self.active_green_lane].state = SignalState.RED
        self.signals[self.active_green_lane].vehicles_served += int(
            self._current_densities[self.active_green_lane]
        )
        self.total_vehicles_served += int(self._current_densities[self.active_green_lane])
        self.cycle_number += 1

        # Increment starvation counters
        for i in range(self.num_lanes):
            if i != self.active_green_lane:
                self.signals[i].cycles_since_green += 1
                self.signals[i].total_wait_time += (
                    self._current_green_remaining + SignalTimingCalculator.YELLOW_DURATION
                )

        # Select next lane: highest priority score
        next_lane = self._select_next_lane()
        density = self._current_densities[next_lane]
        self._start_green(next_lane, density)

    def _select_next_lane(self) -> int:
        """Select next lane using density + fairness scoring."""
        best_lane = 0
        best_score = -1

        for i in range(self.num_lanes):
            if i == self.active_green_lane:
                continue

            density = self._current_densities[i]
            wait_bonus = self.signals[i].cycles_since_green * 5.0
            score = density + wait_bonus

            if score > best_score:
                best_score = score
                best_lane = i

        return best_lane

    def _start_green(self, lane_id: int, density: float):
        """Set a lane to green with optimized duration."""
        timing = SignalTimingCalculator.calculate(density, self.signals[lane_id].cycles_since_green)

        self.active_green_lane = lane_id
        self.signals[lane_id].state = SignalState.GREEN
        self.signals[lane_id].cycles_since_green = 0
        self.signals[lane_id].last_green_timestamp = time.time()
        self._current_green_remaining = timing.green_duration
        self._in_yellow = False

        print(f"[Engine] Lane {lane_id} → GREEN for {timing.green_duration:.1f}s (density={density:.1f})")

    def _force_green(self, lane_id: int):
        """Force a specific lane to green immediately (emergency)."""
        for i in range(self.num_lanes):
            self.signals[i].state = SignalState.EMERGENCY_HOLD if i != lane_id else SignalState.GREEN

        self.active_green_lane = lane_id
        self._current_green_remaining = 9999.0
        self._in_yellow = False
        print(f"[Engine] ⚡ Lane {lane_id} FORCED GREEN (emergency)")

    def stop(self):
        """Stop the engine."""
        self._running = False
