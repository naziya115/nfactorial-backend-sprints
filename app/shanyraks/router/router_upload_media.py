from typing import Any

from fastapi import Depends, Response, UploadFile
from pydantic import Field
from typing import List

from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel

from ..service import Service, get_service

from . import router


@router.post("/{shanyrak_id:str}/media")
def upload_files(
    shanyrak_id: str,
    files: List[UploadFile],
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    result = []
    check = True
    for file in files:
        if file.filename.endswith(".jpg") or file.filename.endswith(".png"):
            image_id = svc.s3_service.upload_file(
                file=file.file, filename=file.filename
            )
            result.append(image_id)
            svc.repository.connect_image_to_shanyrak(
                shanyrak_id=shanyrak_id, image_id=image_id
            )
        else:
            check = False
    return Response(status_code=200) if check else Response(status_code=404)
