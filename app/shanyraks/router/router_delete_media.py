from typing import Any

from fastapi import Depends, Response

from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data

from ..service import Service, get_service

from . import router


@router.delete("/{shanyrak_id:str}/media")
def delete_media(
    shanyrak_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    update_result = svc.repository.update_shanyrak_images(
        shanyrak_id, jwt_data.user_id, {"$unset": {"images": ""}}
    )
    if update_result.modified_count == 1:
        return Response(status_code=200)
    return Response(status_code=404)
