from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.file_upload import FileUploadService

router = APIRouter(prefix="/upload", tags=["File Upload"])

file_service = FileUploadService()


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload image file"""
    try:
        file_path = await file_service.upload_image(file)
        return {
            "message": "Image uploaded successfully",
            "file_path": file_path,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
