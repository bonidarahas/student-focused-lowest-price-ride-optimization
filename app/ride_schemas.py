from pydantic import BaseModel
from typing import List


class RideEstimateRequest(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    is_student: bool = False


class DriverPriceOption(BaseModel):
    driver_id: int
    driver_name: str
    rating: float
    estimated_pickup_minutes: int
    base_price: float
    discount_amount: float
    final_price: float


class RideEstimateResponse(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    is_student: bool
    selected_option: DriverPriceOption
    all_options: List[DriverPriceOption]
    reason: str


class RideBookingRequest(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    is_student: bool = False


class RideBookingResponse(BaseModel):
    booking_id: int
    rider_name: str
    driver_id: int
    driver_name: str
    pickup_location: str
    dropoff_location: str
    final_price: float
    status: str
    reason: str