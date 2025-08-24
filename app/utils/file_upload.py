import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
from app.config import settings


class FileUploadService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "images").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
    
    async def upload_image(self, file: UploadFile, max_size: int = None) -> str:
        """Upload and process image file"""
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size
        max_size = max_size or settings.max_file_size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {max_size} bytes"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["jpg", "jpeg", "png", "gif", "webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image format"
            )
        
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = self.upload_dir / "images" / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Compress image if needed
        await self._compress_image(file_path)
        
        return f"uploads/images/{unique_filename}"
    
    async def _compress_image(self, file_path: Path, max_width: int = 800, quality: int = 85):
        """Compress image to reduce file size"""
        try:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save with compression
                img.save(file_path, optimize=True, quality=quality)
        except Exception:
            # If compression fails, keep original file
            pass
    
    def delete_file(self, file_path: str) -> bool:
        """Delete uploaded file"""
        try:
            full_path = Path(file_path)
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
        except Exception:
            pass
        return False
