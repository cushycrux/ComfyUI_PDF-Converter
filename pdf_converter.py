import os
import sys
import torch
import numpy as np
from PIL import Image
from pathlib import Path
# PDF-Converter by CrushyCrux - This node converts PDF's into png files
# Ensure this module can be found by other imports if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
try:
    import folder_paths
except ImportError:
    print("[PDF-Converter] Warning: folder_paths not found.")
    class MockFolderPaths:
        @staticmethod
        def get_input_directory():
            return os.path.join(os.getcwd(), "input")
        @staticmethod
        def get_output_directory():
            return os.path.join(os.getcwd(), "output")
    folder_paths = MockFolderPaths()
try:
    import fitz
except ImportError:
    raise ImportError(
        "PyMuPDF is not installed. Please install it using:\n"
        "pip install pymupdf\n"
        "Or run the requirements.txt in your ComfyUI environment."
    )
def print_cyan(text):
    print(f"\033[96m{text}\033[0m")
def print_green(text):
    print(f"\033[92m{text}\033[0m")
def print_red(text):
    print(f"\033[91m{text}\033[0m")
class PDFConverter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pdf_folder": ("STRING", {"default": "", "multiline": False}),
                "dpi": ("INT", {
                    "default": 150,
                    "min": 72,
                    "max": 600,
                    "step": 1,
                    "display": "number"
                }),
                "output_folder_name": ("STRING", {"default": "pdf_extracted_images"}),
            },
            "optional": {
                # New: Allows absolute path usage
                "use_absolute_path": ("BOOLEAN", {"default": False}),
                "max_pages_per_pdf": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 99999,
                    "forceInput": True
                })
            }
        }
    CATEGORY = "PDF Utils"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Connect txt output here.",)
    FUNCTION = "load_and_convert"
    def load_and_convert(self, pdf_folder, dpi=150, output_folder_name="pdf_extracted_images", max_pages_per_pdf=-1, use_absolute_path=False):
        try:
            if fitz is None:
                raise ImportError("PyMuPDF (fitz) is not installed.")
            # Determine base path based on absolute or relative setting
            if use_absolute_path:
                base_path = pdf_folder
            else:
                input_dir = folder_paths.get_input_directory()
                base_path = os.path.join(input_dir, pdf_folder)

            print_green(f"DEBUG: Base Path: {base_path}")
            if not os.path.exists(base_path):
                error_msg = f"Error: Folder '{base_path}' does not exist."
                print_red(error_msg)
                return (error_msg,)
            # Output directory is always in ComfyUI's output folder for consistency
            output_dir = folder_paths.get_output_directory()
            output_base_dir = os.path.join(output_dir, output_folder_name)

            pdf_files = []
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))

            print_green(f"DEBUG: Found {len(pdf_files)} PDFs.")
            all_processed = 0

            os.makedirs(output_base_dir, exist_ok=True)
            for pdf_path in pdf_files:
                try:
                    rel_path = os.path.relpath(pdf_path, base_path)
                    pdf_name_without_ext = Path(rel_path).stem

                    output_folder = os.path.join(output_base_dir, pdf_name_without_ext)
                    os.makedirs(output_folder, exist_ok=True)
                    doc = fitz.open(pdf_path)
                    num_pages = len(doc)

                    if max_pages_per_pdf > 0:
                        pages_to_process = range(min(num_pages, max_pages_per_pdf))
                    else:
                        pages_to_process = range(num_pages)
                    for page_num in pages_to_process:
                        page = doc[page_num]

                        zoom = dpi / 72.0
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat)

                        if pix.width == 0 or pix.height == 0:
                            continue
                        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
                        img_tensor = torch.tensor(img_np, dtype=torch.float32) / 255.0
                        filename = f"{pdf_name_without_ext}_page_{page_num + 1}.png"
                        full_img_path = os.path.join(output_base_dir, pdf_name_without_ext, filename)

                        pil_image = Image.fromarray(np.clip(img_tensor.squeeze().numpy() * 255.0, 0, 255).astype(np.uint8))
                        pil_image.save(full_img_path)

                        all_processed += 1
                    doc.close()
                except Exception as e:
                    print_red(f"Error processing PDF {pdf_path}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            success_msg = f"Successfully processed {all_processed} pages."
            print_green(success_msg)
            return (success_msg,)
        except Exception as e:
            error_msg = f"Critical Error in PDFConverter: {e}"
            print_red(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg,)
NODE_CLASS_MAPPINGS = {
    "PDF-Converter": PDFConverter,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "PDF-Converter": "PDF Converter",
}
print("[PDF-Converter] Module loaded successfully.")