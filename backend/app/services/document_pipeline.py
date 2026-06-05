import os
import io
import base64
import logging
from PIL import Image
import fitz  # PyMuPDF — import as fitz, not pymupdf
import pytesseract
from app.core.config import settings

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

logger = logging.getLogger(__name__)

MAX_PAGES = 10
MAX_IMAGE_WIDTH = 1500  # pixels


def _image_to_base64(pil_image: Image.Image) -> str:
    """Convert PIL Image to PNG bytes in memory and return as base64 string."""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _resize_image(pil_image: Image.Image) -> Image.Image:
    """Resize PIL Image proportionally if its width exceeds MAX_IMAGE_WIDTH."""
    if pil_image.width > MAX_IMAGE_WIDTH:
        aspect_ratio = pil_image.height / pil_image.width
        target_height = int(MAX_IMAGE_WIDTH * aspect_ratio)
        pil_image.thumbnail((MAX_IMAGE_WIDTH, target_height))
    return pil_image


def _run_ocr(pil_image: Image.Image) -> str:
    """Run Tesseract OCR on a PIL Image, returning the text or an empty string on failure."""
    try:
        return pytesseract.image_to_string(pil_image, lang="eng")
    except Exception as e:
        logger.warning(f"OCR failed, continuing with vision-only: {e}")
        return ""


def process_documents(file_paths: list[str]) -> dict:
    """Convert uploaded PDF and image files into base64-encoded PNGs and combined OCR text."""
    base64_images = []
    ocr_texts = []
    total_pages = 0

    for file_path in file_paths:
        if total_pages >= MAX_PAGES:
            logger.info("Reached MAX_PAGES limit, skipping remaining files/pages.")
            break

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".pdf":
                with fitz.open(file_path) as doc:
                    for page_num in range(len(doc)):
                        if total_pages >= MAX_PAGES:
                            break

                        page = doc[page_num]
                        
                        # Render page to pixmap at 150 DPI
                        pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                        
                        # Convert pixmap PNG bytes to PIL Image
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        img = _resize_image(img)
                        
                        # Save base64-encoded image
                        base64_images.append(_image_to_base64(img))
                        
                        # Extract digital text if present, otherwise perform OCR
                        text = page.get_text("text")
                        if text.strip():
                            ocr_texts.append(f"--- Page {page_num + 1} ---\n{text}")
                        else:
                            ocr_result = _run_ocr(img)
                            ocr_texts.append(ocr_result)

                        total_pages += 1

            elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                with Image.open(file_path) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    img = _resize_image(img)
                    
                    # Save base64-encoded image
                    base64_images.append(_image_to_base64(img))
                    
                    # Perform OCR
                    ocr_result = _run_ocr(img)
                    ocr_texts.append(ocr_result)
                    
                    total_pages += 1

            else:
                logger.warning(f"Unsupported file type: {file_path}, skipping")
                continue

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            continue

    if not base64_images:
        logger.warning("No images successfully processed, base64_images is empty")

    return {
        "base64_images": base64_images,
        "ocr_text": "\n\n".join(ocr_texts),
        "document_count": len(file_paths),
        "page_count": total_pages
    }
