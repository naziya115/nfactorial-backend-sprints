from fastapi import Depends, Response

from app.utils import AppModel
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from ..service import Service, get_service
from . import router


class AddCommentRequest(AppModel):
    content: str


@router.post("/{shanyrak_id:str}/comments")
def add_comment(
    shanyrak_id: str,
    input: AddCommentRequest,
    svc: Service = Depends(get_service),
    jwt_data: JWTData = Depends(parse_jwt_user_data),
) -> dict[str, str]:
    svc.repository.add_comment(jwt_data.user_id, shanyrak_id, input.dict())

    return Response(status_code=200)
