from typing import Any

from fastapi import Depends, Response
from pydantic import Field
from typing import List

from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel

from ..service import Service, get_service

from . import router


class GetShanyrakResponse(AppModel):
    comments: list[dict]


@router.get("/{shanyrak_id:str}/comments", response_model=GetShanyrakResponse)
def get_comments(
    shanyrak_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    return svc.repository.get_all_comments(shanyrak_id)
