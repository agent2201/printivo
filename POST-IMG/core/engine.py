import os
import subprocess
import sys
from sqlalchemy import create_engine, text

class NexusPrimeEngine:
    """
    Ultimate Image Engine for DTF Prepress.
    Supports Raster (PNG, JPG) and Vector (PDF, EPS, AI).
    Features: Auto-Trim, White Choke, High-Res Rasterization.
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.raw_dir = os.path.join(self.base_dir, "RAW")
        self.processed_dir = os.path.join(self.base_dir, "PROCESSED")
        self.ready_dir = os.path.join(self.base_dir, "READY_TO_PRINT")
        self.db_url = "postgresql://nexus_admin:nexus_password@localhost:5432/nexus_core"

        
        # Ensure Ghostscript is in path for this process
        gs_path = r"C:\Program Files\gs\gs10.03.1\bin"
        if gs_path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + gs_path

        for d in [self.processed_dir, self.ready_dir]:
            os.makedirs(d, exist_ok=True)

    def run_magick(self, args):
        cmd = ["magick"] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Magick Error: {e.stderr}")
            return False

    def process_file(self, filename):
        input_path = os.path.join(self.raw_dir, filename)
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1].lower()
        
        output_tiff = os.path.join(self.processed_dir, f"{base_name}_prime.tiff")
        white_mask = os.path.join(self.processed_dir, f"{base_name}_white_mask.png")
        
        print(f"\n[PRIME v2.1] Processing: {filename}")
        
        is_vector = ext in ['.pdf', '.eps', '.ai', '.svg']
        
        args = []
        if is_vector:
            print("Detected Vector format. Applying High-Density Rasterization (600 DPI)...")
            args.extend(["-density", "600"])
            input_path_fixed = f"{input_path}[0]"
        else:
            input_path_fixed = input_path

        args.extend([input_path_fixed, "-background", "none", "-fuzz", "10%", "-trim", "+repage"])
        
        # 1. Look up requested dimensions from the DB
        try:
            parts = base_name.split('_') # e.g. ["2026-04-15", "4", "original"]
            if len(parts) >= 2 and parts[1].isdigit():
                job_id = int(parts[1])
                engine_db = create_engine(self.db_url)
                with engine_db.connect() as conn:
                    result = conn.execute(text("SELECT width_cm, height_cm FROM print_jobs WHERE id = :id"), {"id": job_id}).fetchone()
                    if result and result[0] and result[1]:
                        w_cm, h_cm = float(result[0]), float(result[1])
                        w_px = int((w_cm / 2.54) * 300)
                        h_px = int((h_cm / 2.54) * 300)
                        print(f"Applying Customer Size Override: {w_cm}x{h_cm} cm -> {w_px}x{h_px} px")
                        # The '!' forces exact resizing regardless of aspect ratio, but let's avoid it to prevent distortion
                        # If we omit '!', ImageMagick fits the image safely INSIDE a bounding box. 
                        # We will use exact dimensions ONLY if the ratio matches, but bounding box is generally safer for DTF prepress.
                        args.extend(["-resize", f"{w_px}x{h_px}"])
        except Exception as e:
            print(f"Failed to apply dimension logic from DB: {e}")
        
        # 2. Apply standard DPI metadata
        args.extend([
            "-units", "PixelsPerInch",
            "-density", "300",
            "-colorspace", "sRGB",
            "-define", "tiff:alpha=associated",
            "-compress", "lzw",
            output_tiff
        ])

        if self.run_magick(args):
            print(f"DONE: TIFF Created: {os.path.basename(output_tiff)}")
            
            # DASHBOARD THUMBNAIL (For visual monitoring only)
            thumb_dir = os.path.join(self.base_dir, "www", "thumbs")
            os.makedirs(thumb_dir, exist_ok=True)
            thumb_path = os.path.join(thumb_dir, f"{base_name}_prime.png")
            print(f"[DASH] Generating Dashboard Icon: {os.path.basename(thumb_path)}")
            self.run_magick([output_tiff, "-resize", "400x400", thumb_path])
            
            # Generate White Choke Mask with Halftoning (Dithering)
            print("[SHIELD] Generating Advanced White Choke + Halftone...")
            mask_args = [
                output_tiff,
                "-alpha", "extract",
                "-negate",
                "-morphology", "Erode", "Diamond:1.5",
                "-ordered-dither", "h6x6a", # Creates professional halftone screening
                "-negate",
                white_mask
            ]
            if self.run_magick(mask_args):
                print(f"DONE: White Mask Created: {os.path.basename(white_mask)}")
        else:
            print(f"ERROR: Failed to process {filename}")

    def run_all(self):
        supported = ('.png', '.jpg', '.jpeg', '.tiff', '.pdf', '.eps', '.ai')
        all_files = [f for f in os.listdir(self.raw_dir) if f.lower().endswith(supported)]
        
        # 1. Distribute files: Originals vs Previews
        originals = [f for f in all_files if "thumb" not in f.lower() and "preview" not in f.lower()]
        previews = [f for f in all_files if "thumb" in f.lower() or "preview" in f.lower()]
        
        # 2. Hand-off previews to Dashboard immediately (Zero-Processing)
        thumb_dir = os.path.join(self.base_dir, "www", "thumbs")
        os.makedirs(thumb_dir, exist_ok=True)
        
        for p in previews:
            # Map thumb name to match the processed TIFF base name for the dashboard
            # Example: 2026-04-14_2_thumb.jpg -> 2026-04-14_2_original_prime.png (or similar)
            # Actually, let's keep it simple: link by prefix
            prefix = "_".join(p.split("_")[:2]) # 2026-04-14_2
            target_thumb = os.path.join(thumb_dir, f"{prefix}_original_prime.png")
            
            if not os.path.exists(target_thumb):
                import shutil
                shutil.copy2(os.path.join(self.raw_dir, p), target_thumb)
                print(f"[FAST-TRACK] Preview used for dashboard: {p}")

        if not originals:
            print(f"No original files to process.")
            return
            
        print(f"Processing {len(originals)} originals. Using {len(previews)} existing previews for dashboard.")
        for f in originals:
            self.process_file(f)

if __name__ == "__main__":
    engine = NexusPrimeEngine()
    engine.run_all()
