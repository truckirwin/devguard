import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
import io
import logging
from sqlalchemy.orm import Session
from app.models.models import PPTFile, SlideImage
from app.db.database import get_db
from sqlalchemy import and_
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

class PPTToPNGConverter:
    """
    Converts PowerPoint files to PNG images using LibreOffice in headless mode.
    Stores the images in PostgreSQL database.
    """
    
    def __init__(self, libreoffice_path: str = None):
        """Initialize converter with optimized settings."""
        self.libreoffice_path = libreoffice_path or self._find_libreoffice()
        # Reduced resolution for faster processing
        self.max_image_width = 960   # Maximum width for main images (50% of 1920)
        self.max_image_height = 540  # Maximum height for main images (50% of 1080)
        self.thumbnail_width = 300  # Thumbnail width
        self.thumbnail_height = 200  # Thumbnail height
        # Optimization settings
        self.dpi = 120  # Reduced from 150 DPI for faster processing
        self.jpeg_quality = 80  # Slightly reduced quality for smaller files
        self.png_quality = 6  # PNG compression level (0-9, higher = smaller)
        
    def _find_libreoffice(self) -> str:
        """Find LibreOffice installation path."""
        possible_paths = [
            # macOS
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            # Linux
            "/usr/bin/libreoffice",
            "/usr/local/bin/libreoffice",
            "/opt/libreoffice/program/soffice",
            # Windows
            "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
            "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found LibreOffice at: {path}")
                return path
                
        # Try to find in PATH
        try:
            result = subprocess.run(["which", "libreoffice"], 
                                  capture_output=True, text=True, check=True)
            path = result.stdout.strip()
            if path:
                logger.info(f"Found LibreOffice in PATH: {path}")
                return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        raise RuntimeError("LibreOffice not found. Please install LibreOffice or provide the path manually.")
    
    def _create_temp_directory(self) -> str:
        """Create a temporary directory for conversion."""
        return tempfile.mkdtemp(prefix="ppt_conversion_")
    
    def _cleanup_temp_directory(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")
    
    def convert_ppt_to_images_optimized(self, ppt_file_path: str, output_dir: str) -> List[str]:
        """
        Optimized PowerPoint to PNG conversion using direct pdftoppm approach.
        
        Args:
            ppt_file_path: Path to the PowerPoint file
            output_dir: Directory to save the converted images
            
        Returns:
            List of paths to generated PNG files
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Convert PPT directly to PDF (single conversion)
            pdf_file = os.path.join(output_dir, "presentation.pdf")
            
            pdf_cmd = [
                self.libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                ppt_file_path
            ]
            
            logger.info(f"Converting PPT to PDF: {' '.join(pdf_cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                pdf_cmd,
                capture_output=True,
                text=True,
                timeout=180,  # Reduced timeout
                check=True
            )
            
            conversion_time = time.time() - start_time
            logger.info(f"PDF conversion completed in {conversion_time:.2f}s")
            
            # Find the generated PDF file
            pdf_files = [f for f in os.listdir(output_dir) if f.lower().endswith('.pdf')]
            if not pdf_files:
                raise RuntimeError("No PDF file was generated from PowerPoint conversion")
            
            pdf_file_path = os.path.join(output_dir, pdf_files[0])
            
            # Step 2: Use pdftoppm for faster, direct PDF to PNG conversion
            base_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
            
            try:
                # Optimized pdftoppm command with reduced DPI and JPEG format for speed
                pdftoppm_cmd = [
                    "pdftoppm",
                    "-jpeg",  # Use JPEG instead of PNG for faster processing
                    "-jpegopt", f"quality={self.jpeg_quality}",
                    "-r", str(self.dpi),  # Reduced DPI for speed
                    "-cropbox",  # Use crop box for better slide boundaries
                    pdf_file_path,
                    os.path.join(output_dir, f"{base_name}")
                ]
                
                logger.info(f"Converting PDF to images with pdftoppm: {' '.join(pdftoppm_cmd)}")
                start_time = time.time()
                
                result = subprocess.run(
                    pdftoppm_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,  # Reduced timeout
                    check=True
                )
                
                conversion_time = time.time() - start_time
                logger.info(f"pdftoppm conversion completed in {conversion_time:.2f}s")
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.warning(f"pdftoppm failed: {e}, falling back to ImageMagick...")
                
                # Fallback to ImageMagick with optimized settings
                try:
                    convert_cmd = [
                        "convert",
                        "-density", str(self.dpi),
                        "-quality", str(self.jpeg_quality),
                        "-format", "jpg",
                        pdf_file_path,
                        os.path.join(output_dir, f"{base_name}-%02d.jpg")
                    ]
                    
                    logger.info(f"Using ImageMagick convert: {' '.join(convert_cmd)}")
                    start_time = time.time()
                    
                    result = subprocess.run(
                        convert_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=True
                    )
                    
                    conversion_time = time.time() - start_time
                    logger.info(f"ImageMagick conversion completed in {conversion_time:.2f}s")
                    
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    logger.error(f"All conversion methods failed: {e}")
                    raise RuntimeError(f"Image conversion failed: {e}")
            
            # Find generated image files (now JPEGs)
            image_files = []
            for file in os.listdir(output_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_files.append(os.path.join(output_dir, file))
            
            # Sort files to ensure proper slide order
            image_files.sort()
            
            logger.info(f"Generated {len(image_files)} image files: {[os.path.basename(f) for f in image_files]}")
            return image_files
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("PowerPoint conversion timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"PowerPoint conversion failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Conversion error: {str(e)}")

    def _process_single_image(self, image_path: str, slide_number: int) -> Tuple[int, bytes, bytes, int, int]:
        """
        Process a single image file and return optimized data.
        
        Returns:
            Tuple of (slide_number, image_bytes, thumbnail_bytes, width, height)
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_size = img.size
                
                # Resize main image if too large
                main_img = img.copy()
                if main_img.width > self.max_image_width or main_img.height > self.max_image_height:
                    main_img.thumbnail((self.max_image_width, self.max_image_height), Image.Resampling.LANCZOS)
                
                # Create optimized main image (using JPEG for smaller size)
                main_byte_array = io.BytesIO()
                main_img.save(main_byte_array, format='JPEG', quality=self.jpeg_quality, optimize=True)
                main_bytes = main_byte_array.getvalue()
                
                # Create thumbnail
                thumb_img = img.copy()
                thumb_img.thumbnail((self.thumbnail_width, self.thumbnail_height), Image.Resampling.LANCZOS)
                
                thumb_byte_array = io.BytesIO()
                thumb_img.save(thumb_byte_array, format='JPEG', quality=75, optimize=True)
                thumb_bytes = thumb_byte_array.getvalue()
                
                return slide_number, main_bytes, thumb_bytes, main_img.width, main_img.height
                
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            raise

    def convert_and_store_ppt_parallel(self, ppt_file_id: int, ppt_file_path: str, db: Session, max_workers: int = 4) -> int:
        """
        Convert PowerPoint file to images with parallel processing and bulk database operations.
        
        Args:
            ppt_file_id: ID of the PPTFile record
            ppt_file_path: Path to the PowerPoint file
            db: Database session
            max_workers: Number of parallel processing threads
            
        Returns:
            Number of slides converted
        """
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = self._create_temp_directory()
            
            # Convert PPT to images using optimized method
            logger.info(f"Starting optimized conversion for PPT file {ppt_file_id}")
            start_time = time.time()
            
            image_paths = self.convert_ppt_to_images_optimized(ppt_file_path, temp_dir)
            
            if not image_paths:
                raise RuntimeError("No images were generated from the PowerPoint file")
            
            conversion_time = time.time() - start_time
            logger.info(f"Image conversion completed in {conversion_time:.2f}s for {len(image_paths)} slides")
            
            # Delete existing slide images for this PPT file
            db.query(SlideImage).filter(SlideImage.ppt_file_id == ppt_file_id).delete()
            
            # Process images in parallel
            logger.info(f"Processing {len(image_paths)} images with {max_workers} workers")
            start_time = time.time()
            
            slide_records = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all image processing tasks
                future_to_slide = {
                    executor.submit(self._process_single_image, image_path, i): i
                    for i, image_path in enumerate(image_paths, 1)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_slide):
                    slide_number = future_to_slide[future]
                    try:
                        slide_num, image_bytes, thumbnail_bytes, width, height = future.result()
                        
                        # Create database record (don't add to session yet)
                        slide_image = SlideImage(
                            ppt_file_id=ppt_file_id,
                            slide_number=slide_num,
                            image_data=image_bytes,
                            image_format="JPEG",  # Changed to JPEG for smaller size
                            width=width,
                            height=height,
                            thumbnail_data=thumbnail_bytes
                        )
                        
                        slide_records.append(slide_image)
                        
                        logger.info(f"Processed slide {slide_num}: {width}x{height} pixels, "
                                  f"{len(image_bytes)} bytes main, {len(thumbnail_bytes)} bytes thumbnail")
                        
                    except Exception as e:
                        logger.error(f"Failed to process slide {slide_number}: {e}")
                        continue
            
            processing_time = time.time() - start_time
            logger.info(f"Parallel image processing completed in {processing_time:.2f}s")
            
            # Bulk insert all records
            if slide_records:
                logger.info(f"Bulk inserting {len(slide_records)} slide records")
                start_time = time.time()
                
                db.add_all(slide_records)
                db.commit()
                
                db_time = time.time() - start_time
                logger.info(f"Database bulk insert completed in {db_time:.2f}s")
            
            total_time = conversion_time + processing_time + db_time
            logger.info(f"Successfully converted and stored {len(slide_records)} slides for PPT file {ppt_file_id} in {total_time:.2f}s total")
            return len(slide_records)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to convert PPT file {ppt_file_id}: {e}")
            raise
        finally:
            if temp_dir:
                self._cleanup_temp_directory(temp_dir)

    # Keep the original methods for backward compatibility
    convert_ppt_to_images = convert_ppt_to_images_optimized
    
    def _optimize_image(self, image_path: str) -> Tuple[bytes, int, int]:
        """
        Optimize image size and return as bytes.
        
        Returns:
            Tuple of (image_bytes, width, height)
        """
        _, image_bytes, _, width, height = self._process_single_image(image_path, 1)
        return image_bytes, width, height
    
    def _create_thumbnail(self, image_path: str) -> bytes:
        """
        Create a thumbnail version of the image.
        
        Returns:
            Thumbnail image as bytes
        """
        _, _, thumbnail_bytes, _, _ = self._process_single_image(image_path, 1)
        return thumbnail_bytes
    
    def get_slide_image(self, ppt_file_id: int, slide_number: int, db: Session, thumbnail: bool = False) -> Optional[bytes]:
        """
        Retrieve a slide image from the database.
        
        Args:
            ppt_file_id: ID of the PPT file
            slide_number: Slide number (1-based)
            db: Database session
            thumbnail: If True, return thumbnail instead of full image
            
        Returns:
            Image bytes or None if not found
        """
        logger.info(f"🔍 IMAGE REQUEST: PPT {ppt_file_id}, slide {slide_number}, thumbnail={thumbnail}")
        
        slide_image = db.query(SlideImage).filter(
            SlideImage.ppt_file_id == ppt_file_id,
            SlideImage.slide_number == slide_number
        ).first()
        
        if slide_image:
            if thumbnail and slide_image.thumbnail_data:
                logger.info(f"✅ CACHE HIT: PPT {ppt_file_id}, slide {slide_number} thumbnail served from DB cache ({len(slide_image.thumbnail_data)} bytes)")
                return slide_image.thumbnail_data
            elif not thumbnail and slide_image.image_data:
                logger.info(f"✅ CACHE HIT: PPT {ppt_file_id}, slide {slide_number} full image served from DB cache ({len(slide_image.image_data)} bytes)")
                return slide_image.image_data
            else:
                logger.warning(f"⚠️ PARTIAL CACHE: PPT {ppt_file_id}, slide {slide_number} found but {'thumbnail' if thumbnail else 'image'} data missing")
                return None
        else:
            logger.warning(f"❌ CACHE MISS: PPT {ppt_file_id}, slide {slide_number} not found in database cache")
            return None
    
    def get_all_slide_images(self, ppt_file_id: int, db: Session, thumbnail: bool = False) -> List[Tuple[int, bytes]]:
        """
        Retrieve all slide images for a PPT file.
        
        Args:
            ppt_file_id: ID of the PPT file
            db: Database session
            thumbnail: If True, return thumbnails instead of full images
            
        Returns:
            List of tuples (slide_number, image_bytes)
        """
        slide_images = db.query(SlideImage).filter(
            SlideImage.ppt_file_id == ppt_file_id
        ).order_by(SlideImage.slide_number).all()
        
        return [
            (img.slide_number, img.thumbnail_data if thumbnail else img.image_data)
            for img in slide_images
        ]

# Example usage functions
def check_libreoffice_installation() -> bool:
    """Check if LibreOffice is properly installed."""
    try:
        converter = PPTToPNGConverter()
        return True
    except RuntimeError:
        return False

def install_libreoffice_instructions() -> str:
    """Return installation instructions for LibreOffice."""
    return """
To install LibreOffice:

macOS:
  brew install --cask libreoffice
  OR download from: https://www.libreoffice.org/download/download/

Linux (Ubuntu/Debian):
  sudo apt-get update
  sudo apt-get install libreoffice

Linux (CentOS/RHEL):
  sudo yum install libreoffice
  OR sudo dnf install libreoffice

Windows:
  Download from: https://www.libreoffice.org/download/download/
  Run the installer and follow the prompts.

After installation, restart your application.
""" 