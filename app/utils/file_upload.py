import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import uuid
from datetime import datetime

class FileUpload:
    def __init__(self):
        self.upload_dir = "uploads"
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        self.max_size = 5 * 1024 * 1024  # 5MB

    def ensure_directory(self, directory: str):
        """Create directory if it doesn't exist"""
        Path(directory).mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> bool:
        """Validate file type and size"""
        # Check extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")
        
        # Check size (if file is already read)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > self.max_size:
            raise HTTPException(status_code=400, detail=f"File size {size} exceeds limit")
        
        return True

    def generate_filename(self, original_filename: str) -> str:
        """Generate unique filename"""
        ext = os.path.splitext(original_filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{ext}"

    def optimize_image(self, file_path: str, max_width: int = 1920, quality: int = 85):
        """Optimize image size"""
        try:
            with Image.open(file_path) as img:
                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(file_path, optimize=True, quality=quality)
        except Exception as e:
            print(f"Error optimizing image: {e}")

    async def save_file(self, file: UploadFile, sub_directory: str = "") -> str:
        """Save uploaded file to server"""
        self.validate_file(file)
        
        # Create directory
        upload_path = os.path.join(self.upload_dir, sub_directory)
        self.ensure_directory(upload_path)
        
        # Generate filename
        filename = self.generate_filename(file.filename)
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Optimize image
            self.optimize_image(file_path)
            
            # Return relative path
            return os.path.join(sub_directory, filename).replace("\\", "/")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    async def save_multiple_files(self, files: List[UploadFile], sub_directory: str = "") -> List[str]:
        """Save multiple files"""
        saved_paths = []
        for file in files:
            if file and file.filename:
                path = await self.save_file(file, sub_directory)
                saved_paths.append(path)
        return saved_paths

    def delete_file(self, file_path: str):
        """Delete a file"""
        if file_path:
            full_path = os.path.join(self.upload_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        return False

    def delete_multiple_files(self, file_paths: List[str]):
        """Delete multiple files"""
        for file_path in file_paths:
            self.delete_file(file_path)

file_upload = FileUpload()