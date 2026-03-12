"""
Vehicle Detector Module
Uses YOLOv8 to detect vehicles and classify them including emergency vehicles.
Provides per-lane traffic density calculations.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time
import random
import math

# Vehicle class IDs in COCO dataset used by YOLO
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

EMERGENCY_CLASSES = {
    "ambulance": "ambulance",
    "fire truck": "fire_truck",
    "police": "police_car",
}

# Weights for traffic density calculation
VEHICLE_WEIGHTS = {
    "car": 1.0,
    "motorcycle": 0.5,
    "bus": 2.5,
    "truck": 2.0,
    "ambulance": 0.0,   # excluded from density - handled separately
    "fire_truck": 0.0,
    "police_car": 0.0,
}


@dataclass
class DetectedVehicle:
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    center: tuple
    is_emergency: bool = False
    lane_id: Optional[int] = None
    track_id: Optional[int] = None


@dataclass
class LaneDetectionResult:
    lane_id: int
    vehicle_count: int
    weighted_density: float
    vehicles: list
    has_emergency: bool = False
    emergency_vehicles: list = field(default_factory=list)
    congestion_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    frame_timestamp: float = 0.0


@dataclass
class FrameDetectionResult:
    lanes: list  # List[LaneDetectionResult]
    total_vehicles: int
    total_density: float
    emergency_detected: bool
    emergency_vehicles: list
    processing_time_ms: float
    frame_id: int
    annotated_frame: Optional[np.ndarray] = None


class TrafficDensityCalculator:
    """Calculates traffic density scores from vehicle detections."""

    DENSITY_THRESHOLDS = {
        "LOW": (0, 5),
        "MEDIUM": (5, 15),
        "HIGH": (15, 30),
        "CRITICAL": (30, float("inf")),
    }

    @staticmethod
    def get_congestion_level(weighted_count: float) -> str:
        for level, (low, high) in TrafficDensityCalculator.DENSITY_THRESHOLDS.items():
            if low <= weighted_count < high:
                return level
        return "CRITICAL"

    @staticmethod
    def calculate_lane_density(vehicles: list) -> float:
        total = 0.0
        for v in vehicles:
            if not v.is_emergency:
                weight = VEHICLE_WEIGHTS.get(v.class_name, 1.0)
                total += weight * v.confidence
        return round(total, 2)


class LaneZoneMapper:
    """Maps detections to lane zones based on frame geometry."""

    def __init__(self, frame_width: int, frame_height: int, num_lanes: int = 4):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_lanes = num_lanes
        self.lane_width = frame_width // num_lanes

    def get_lane_id(self, center_x: float) -> int:
        lane = int(center_x / self.lane_width)
        return min(lane, self.num_lanes - 1)

    def get_lane_boundaries(self, lane_id: int) -> tuple:
        x1 = lane_id * self.lane_width
        x2 = x1 + self.lane_width
        return (x1, 0, x2, self.frame_height)


class VehicleDetector:
    """
    Main vehicle detection class.
    Uses YOLOv8 when available, falls back to simulation for demo purposes.
    """

    def __init__(self, model_path: str = "yolov8n.pt", num_lanes: int = 4,
                 confidence_threshold: float = 0.45, use_simulation: bool = False):
        self.num_lanes = num_lanes
        self.confidence_threshold = confidence_threshold
        self.use_simulation = use_simulation
        self.model = None
        self.frame_id = 0
        self.density_calculator = TrafficDensityCalculator()

        if not use_simulation:
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print(f"[VehicleDetector] YOLO model loaded: {model_path}")
            except Exception as e:
                print(f"[VehicleDetector] YOLO unavailable ({e}), switching to simulation mode.")
                self.use_simulation = True

        if self.use_simulation:
            print("[VehicleDetector] Running in SIMULATION mode.")

    def detect_frame(self, frame: np.ndarray) -> FrameDetectionResult:
        """Process a single frame and return detection results."""
        t0 = time.perf_counter()
        self.frame_id += 1

        h, w = frame.shape[:2]
        lane_mapper = LaneZoneMapper(w, h, self.num_lanes)

        if self.use_simulation:
            detections = self._simulate_detections(w, h)
        else:
            detections = self._run_yolo(frame, lane_mapper)

        # Assign lanes
        for v in detections:
            v.lane_id = lane_mapper.get_lane_id(v.center[0])

        # Group by lane
        lane_results = []
        for lane_id in range(self.num_lanes):
            lane_vehicles = [v for v in detections if v.lane_id == lane_id]
            normal_vehicles = [v for v in lane_vehicles if not v.is_emergency]
            emergency_vehicles = [v for v in lane_vehicles if v.is_emergency]
            weighted_density = self.density_calculator.calculate_lane_density(lane_vehicles)
            congestion = TrafficDensityCalculator.get_congestion_level(weighted_density)

            lane_results.append(LaneDetectionResult(
                lane_id=lane_id,
                vehicle_count=len(normal_vehicles),
                weighted_density=weighted_density,
                vehicles=lane_vehicles,
                has_emergency=len(emergency_vehicles) > 0,
                emergency_vehicles=emergency_vehicles,
                congestion_level=congestion,
                frame_timestamp=time.time(),
            ))

        all_emergency = [v for v in detections if v.is_emergency]
        total_density = sum(lr.weighted_density for lr in lane_results)

        annotated = self._annotate_frame(frame.copy(), lane_results, lane_mapper)

        processing_ms = (time.perf_counter() - t0) * 1000

        return FrameDetectionResult(
            lanes=lane_results,
            total_vehicles=len([v for v in detections if not v.is_emergency]),
            total_density=round(total_density, 2),
            emergency_detected=len(all_emergency) > 0,
            emergency_vehicles=all_emergency,
            processing_time_ms=round(processing_ms, 1),
            frame_id=self.frame_id,
            annotated_frame=annotated,
        )

    def _run_yolo(self, frame: np.ndarray, lane_mapper: LaneZoneMapper) -> list:
        """Run actual YOLOv8 inference."""
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cls_name = self.model.names[cls_id].lower()

                is_emergency = any(e in cls_name for e in EMERGENCY_CLASSES)
                if cls_id in VEHICLE_CLASSES or is_emergency:
                    display_name = cls_name
                    for key in EMERGENCY_CLASSES:
                        if key in cls_name:
                            display_name = EMERGENCY_CLASSES[key]
                            break

                    detections.append(DetectedVehicle(
                        class_name=display_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=(cx, cy),
                        is_emergency=is_emergency,
                    ))
        return detections

    def _simulate_detections(self, width: int, height: int) -> list:
        """Generate realistic simulated detections for demo."""
        detections = []
        lane_width = width // self.num_lanes

        # Simulate variable traffic per lane
        base_counts = [
            random.randint(2, 25),
            random.randint(0, 10),
            random.randint(5, 30),
            random.randint(1, 15),
        ]

        vehicle_types = ["car"] * 10 + ["truck"] * 2 + ["bus"] * 1 + ["motorcycle"] * 3

        track_id = 1
        for lane_id, count in enumerate(base_counts[:self.num_lanes]):
            lane_x_start = lane_id * lane_width
            for _ in range(count):
                vtype = random.choice(vehicle_types)
                cx = random.randint(lane_x_start + 10, lane_x_start + lane_width - 10)
                cy = random.randint(50, height - 50)
                w_box = random.randint(40, 80)
                h_box = random.randint(30, 60)
                conf = random.uniform(0.5, 0.98)

                detections.append(DetectedVehicle(
                    class_name=vtype,
                    confidence=round(conf, 2),
                    bbox=(cx - w_box // 2, cy - h_box // 2, cx + w_box // 2, cy + h_box // 2),
                    center=(cx, cy),
                    is_emergency=False,
                    track_id=track_id,
                ))
                track_id += 1

        # Random emergency vehicle (5% chance per frame)
        if random.random() < 0.05:
            lane_id = random.randint(0, self.num_lanes - 1)
            cx = lane_id * lane_width + lane_width // 2
            cy = random.randint(50, height - 50)
            detections.append(DetectedVehicle(
                class_name="ambulance",
                confidence=0.95,
                bbox=(cx - 45, cy - 30, cx + 45, cy + 30),
                center=(cx, cy),
                is_emergency=True,
                track_id=track_id,
            ))

        return detections

    def _annotate_frame(self, frame: np.ndarray, lane_results: list, lane_mapper: LaneZoneMapper) -> np.ndarray:
        """Draw bounding boxes, lane overlays, and info on frame."""
        h, w = frame.shape[:2]

        # Draw lane dividers
        for i in range(1, self.num_lanes):
            x = i * lane_mapper.lane_width
            cv2.line(frame, (x, 0), (x, h), (200, 200, 200), 1, cv2.LINE_AA)

        for lr in lane_results:
            # Lane background tint by congestion
            x1, _, x2, _ = lane_mapper.get_lane_boundaries(lr.lane_id)
            color_map = {
                "LOW": (0, 80, 0),
                "MEDIUM": (0, 80, 80),
                "HIGH": (80, 60, 0),
                "CRITICAL": (80, 0, 0),
            }
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, 0), (x2, h), color_map.get(lr.congestion_level, (0, 0, 0)), -1)
            cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)

            # Draw each vehicle
            for v in lr.vehicles:
                bx1, by1, bx2, by2 = v.bbox
                if v.is_emergency:
                    color = (0, 50, 255)
                    thickness = 3
                elif lr.congestion_level == "CRITICAL":
                    color = (0, 0, 200)
                elif lr.congestion_level == "HIGH":
                    color = (0, 140, 255)
                elif lr.congestion_level == "MEDIUM":
                    color = (0, 200, 200)
                else:
                    color = (0, 200, 50)

                cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)
                label = f"{v.class_name} {v.confidence:.2f}"
                cv2.putText(frame, label, (bx1, by1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

            # Lane info overlay
            lx = x1 + 5
            cy_info = 20
            cv2.putText(frame, f"Lane {lr.lane_id + 1}", (lx, cy_info),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"{lr.congestion_level}", (lx, cy_info + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (50, 255, 50) if lr.congestion_level == "LOW" else (50, 50, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Density: {lr.weighted_density:.1f}", (lx, cy_info + 44),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

        return frame
