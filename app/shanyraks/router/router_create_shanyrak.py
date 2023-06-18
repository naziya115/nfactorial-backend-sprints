from typing import Any
from datetime import datetime
from fastapi import Depends
from pydantic import Field
from typing import List, Optional
from app.utils import AppModel
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data

from ..service import Service, get_service

from . import router


class CreateShanyrakRequest(AppModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class CreateShanyrakResponse(AppModel):
    id: Any = Field(alias="_id")


@router.post("/", response_model=CreateShanyrakResponse)
def create_shanyrak(
    input: CreateShanyrakRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    combined_data = input.dict() | svc.here_service.get_coordinates(input.address)
    inserted_id = svc.repository.create_shanyrak(jwt_data.user_id, combined_data)
    return CreateShanyrakResponse(id=inserted_id)


# pagination + search
class Shanyrak(AppModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    location: Any
    description: str


class GetShanyrakResponse(AppModel):
    total: int
    objects: List[Shanyrak]


@router.get("/", response_model=GetShanyrakResponse)
def get_shanyraks_by_parameters(
    limit: int,
    offset: int,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,
    rooms_count: Optional[int] = None,
    type: Optional[str] = None,
    price_from: Optional[int] = None,
    price_until: Optional[int] = None,
    svc: Service = Depends(get_service),
):
    result = svc.repository.get_shanyraks_by_parameters(
        limit,
        offset,
        latitude,
        longitude,
        radius,
        rooms_count,
        type,
        price_from,
        price_until,
    )
    return result
