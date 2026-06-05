import os
import pytest
from PIL import Image
import fitz  # PyMuPDF
from app.services.document_pipeline import process_documents, MAX_PAGES, MAX_IMAGE_WIDTH


@pytest.fixture
def temp_files(tmp_path):
    """Fixture to create temporary PDF and image files for testing."""
    # 1. Create a dummy PNG image with text (though Tesseract might not read it, we verify OCR output format)
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(img_path)

    # 2. Create a dummy PDF with text
    pdf_path = tmp_path / "test_doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello from PyMuPDF digital text!")
    doc.save(str(pdf_path))
    doc.close()

    # 3. Create a large image to verify resizing
    large_img_path = tmp_path / "large_image.png"
    large_img = Image.new("RGB", (MAX_IMAGE_WIDTH + 500, 800), color="blue")
    large_img.save(large_img_path)

    return {
        "png": str(img_path),
        "pdf": str(pdf_path),
        "large_png": str(large_img_path),
    }


def test_process_documents_success(temp_files):
    """Test processing a mix of supported files."""
    file_paths = [temp_files["pdf"], temp_files["png"]]
    result = process_documents(file_paths)

    assert isinstance(result, dict)
    assert "base64_images" in result
    assert "ocr_text" in result
    assert "document_count" in result
    assert "page_count" in result

    assert result["document_count"] == 2
    assert result["page_count"] == 2  # 1 page PDF + 1 PNG
    assert len(result["base64_images"]) == 2

    # Check that PDF text was successfully extracted
    assert "Hello from PyMuPDF digital text!" in result["ocr_text"]


def test_process_documents_resizing(temp_files):
    """Test that large images are resized proportionally."""
    file_paths = [temp_files["large_png"]]
    result = process_documents(file_paths)

    assert result["page_count"] == 1
    assert len(result["base64_images"]) == 1

    # To check if it was resized, we can decode and check the image dimensions
    import base64
    import io
    img_data = base64.b64decode(result["base64_images"][0])
    img = Image.open(io.BytesIO(img_data))
    assert img.width == MAX_IMAGE_WIDTH
    # Aspect ratio: original was (MAX_IMAGE_WIDTH + 500) x 800 -> 2000x800.
    # Scaled down to 1500, target height should be 1500 * (800 / 2000) = 600.
    assert img.height == 600


def test_process_documents_max_pages_limit(temp_files, tmp_path):
    """Test that the pipeline stops processing after MAX_PAGES."""
    # Create a PDF with 12 pages
    pdf_path = tmp_path / "many_pages.pdf"
    doc = fitz.open()
    for i in range(12):
        page = doc.new_page()
        page.insert_text((50, 50), f"Digital text on page {i + 1}")
    doc.save(str(pdf_path))
    doc.close()

    result = process_documents([str(pdf_path)])
    assert result["page_count"] == MAX_PAGES
    assert len(result["base64_images"]) == MAX_PAGES
    assert f"Page {MAX_PAGES}" in result["ocr_text"]
    assert f"Page {MAX_PAGES + 1}" not in result["ocr_text"]


def test_process_documents_unsupported_file(temp_files, tmp_path):
    """Test that unsupported files are skipped and logged, but don't crash the pipeline."""
    unsupported_path = tmp_path / "test.txt"
    unsupported_path.write_text("plain text file")

    file_paths = [temp_files["pdf"], str(unsupported_path)]
    result = process_documents(file_paths)

    assert result["document_count"] == 2
    assert result["page_count"] == 1  # only PDF processed
    assert len(result["base64_images"]) == 1
    assert "Hello from PyMuPDF digital text!" in result["ocr_text"]


def test_process_documents_empty_file_list():
    """Test processing an empty list of file paths."""
    result = process_documents([])
    assert result["document_count"] == 0
    assert result["page_count"] == 0
    assert result["base64_images"] == []
    assert result["ocr_text"] == ""
