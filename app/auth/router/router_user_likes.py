from typing import Any

from fastapi import Depends, Response
from fastapi.responses import JSONResponse
from pydantic import Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


@router.get("/auth/users/favorites/shanyraks/{shanyrak_id:str}")
def set_like(
    shanyrak_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    user = svc.repository.set_user_likes(
        user_id=jwt_data.user_id, shanyrak_id=shanyrak_id
    )
    return Response(status_code=200)


class ShnayraksResponse(AppModel):
    id: Any = Field(alias="_id")
    address: str


class Shanyraks(AppModel):
    shanyraks: list[ShnayraksResponse]


@router.get("/auth/users/favorites/shanyraks/", response_model=Shanyraks)
def get_like(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    likes = svc.repository.get_shanyraks_by_id(jwt_data.user_id)
    return Shanyraks(shanyraks=likes)

@router.delete("/auth/users/favorites/shanyraks/{shanyrak_id:str}")
def remove_like(
    shanyrak_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    svc.repository.remove_user_likes(jwt_data.user_id, shanyrak_id)
    return Response(status_code=200)
