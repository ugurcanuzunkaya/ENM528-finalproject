from dataclasses import dataclass
from typing import List


@dataclass
class VehicleType:
    name: str
    capacity: int
    cost_factor: float = 1.0
    color: str = "blue"  # For plotting


# Predefined Types
E_BIKE = VehicleType("E-Bike", capacity=10, cost_factor=0.5, color="#2ca02c")  # Green
E_SCOOTER = VehicleType(
    "E-Scooter", capacity=5, cost_factor=0.3, color="#ff7f0e"
)  # Orange
E_CAR = VehicleType("E-Car", capacity=30, cost_factor=1.0, color="#1f77b4")  # Blue
DIESEL_CAR = VehicleType(
    "Diesel Car", capacity=40, cost_factor=1.5, color="#d62728"
)  # Red


def create_fleet(mode: str) -> List[VehicleType]:
    """
    Returns a list of VehicleTypes based on the mode.
    Mode can be: 'homog' (Standard 4 E-Cars) or 'mix_1' (Custom Mix)
    """
    if mode == "homog":
        # 4 Standard Vehicles (like Baseline)
        return [E_CAR for _ in range(4)]

    elif mode == "mix_1":
        # 1 Diesel, 1 E-Car, 2 E-Bikes
        return [DIESEL_CAR, E_CAR, E_BIKE, E_BIKE]

    elif mode == "mix_2":
        # 4 Scooters, 2 Bikes
        return [E_SCOOTER] * 4 + [E_BIKE] * 2

    else:
        raise ValueError(f"Unknown fleet mode: {mode}")
