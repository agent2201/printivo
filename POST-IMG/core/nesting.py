import os
import subprocess
from PIL import Image
from sqlalchemy import create_engine, text
Image.MAX_IMAGE_PIXELS = None

class NexusNestingEngine:
    def __init__(self, roll_width_cm=60, dpi=300):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.processed_dir = os.path.join(self.base_dir, "PROCESSED")
        self.ready_dir = os.path.join(self.base_dir, "READY_TO_PRINT")
        self.db_url = "postgresql://nexus_admin:nexus_password@localhost:5432/nexus_core"
        
        # Calculate roll width in pixels
        self.roll_width_px = int((roll_width_cm / 2.54) * dpi)
        self.dpi = dpi
        self.margin_px = int((0.5 / 2.54) * dpi) # 5mm margin

    def run_all_orders_data(self):
        # Fetch detailed order data from Postgres
        orders_db = {}
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                # We assume print_jobs table has: filename, quantity, order_id, status
                result = conn.execute(text("SELECT id, file_path, quantity, order_id, status FROM print_jobs"))
                for row in result:
                    if not row[1]: continue
                    # Find folder ID from something like nexus-uploads/2026-04-14_2/original.png
                    parts = row[1].split('/')
                    folder_id = parts[1] if len(parts) > 1 else row[1]
                    orders_db[folder_id] = {
                        "id": row[0],
                        "order_id": row[3] if row[3] is not None else "N/A",
                        "qty": row[2],
                        "status": row[4] if row[4] is not None else "pending"
                    }
        except Exception as e:
            print(f"DB Error fetching extended data: {e}")
        return orders_db

    def run_nesting(self):
        orders_db = self.run_all_orders_data()
        
        # Find all processed tiff files (color)
        files = [f for f in os.listdir(self.processed_dir) if f.endswith("_prime.tiff")]
        if not files:
            print("No processed files found for nesting.")
            return

        images = []
        max_allowed_w = self.roll_width_px - (self.margin_px * 2)

        for f in files:
            folder_id = "_".join(f.split("_")[:2]) # e.g. 2026-04-13_8
            db_info = orders_db.get(folder_id, {"id": 0, "qty": 1, "order_id": "N/A", "status": "pending"})
            
            # Skip files that are not supposed to be in nesting anymore
            current_status = db_info.get("status", "pending")
            if current_status in ["return", "returned", "print", "dispatch", "done", "completed"]:
                continue
                
            qty = db_info.get("qty", 1)

            path = os.path.join(self.processed_dir, f)
            img = Image.open(path)
            if img.mode != 'RGBA': img = img.convert('RGBA')
            
            if img.width > max_allowed_w:
                ratio = max_allowed_w / float(img.width)
                new_h = int(float(img.height) * ratio)
                img = img.resize((max_allowed_w, new_h), Image.Resampling.LANCZOS)

            for _ in range(qty):
                images.append({
                    "name": f, 
                    "img": img, 
                    "w": img.width, 
                    "h": img.height, 
                    "order_id": db_info["order_id"],
                    "folder_id": folder_id
                })

        # PARALLEL FLOW: Sort by Order ID (match site queue) instead of efficiency
        # This keeps all designs of one order grouped together on the roll
        def sort_key(x):
            oid = str(x.get('order_id', '0'))
            fname = x.get('name', '')
            return (oid, fname)

        images.sort(key=sort_key)

        print(f"Starting Nesting for {len(images)} items. Roll Width: {self.roll_width_px}px")

        if not images:
            print("No items to nest. Returning early.")
            nesting_data = {
                "roll_width_px": self.roll_width_px,
                "roll_height_px": 0,
                "dpi": self.dpi,
                "efficiency_pct": 0,
                "items": []
            }
            import json
            with open(os.path.join(self.ready_dir, "nesting_data.json"), "w") as f:
                json.dump(nesting_data, f, indent=2)
            return

        # Simple Shelf Packing

        shelves = []
        current_y = 0
        
        # New Roll Canvas (Initial height 1000px, will grow)
        # We start with a large enough blank canvas but we'll crop it later
        roll_height = sum(img['h'] for img in images) + 2000 # Rough estimate
        full_roll = Image.new("RGBA", (self.roll_width_px, roll_height), (0, 0, 0, 0))

        current_shelf_h = 0
        current_x = 0
        current_y = 0
        
        max_y_reached = 0

        for item in images:
            # If item too wide for current shelf, start new shelf
            if current_x + item['w'] + self.margin_px > self.roll_width_px:
                current_y += current_shelf_h + self.margin_px
                current_x = 0
                current_shelf_h = 0

            # Paste item
            item['x'] = current_x
            item['y'] = current_y
            full_roll.paste(item['img'], (current_x, current_y), item['img'])
            
            # Update shelf stats
            current_x += item['w'] + self.margin_px
            current_shelf_h = max(current_shelf_h, item['h'])
            max_y_reached = max(max_y_reached, current_y + current_shelf_h)

        # Crop to actual used height
        final_roll = full_roll.crop((0, 0, self.roll_width_px, max_y_reached))
        
        # Save Final Roll
        output_path = os.path.join(self.ready_dir, "FINAL_ROLL_FOR_PRINT.tiff")
        final_roll.save(output_path, compression='tiff_lzw', dpi=(self.dpi, self.dpi))
        
        # EXPORT JSON for Dashboard
        total_items_area = sum(item['w'] * item['h'] for item in images)
        roll_area = self.roll_width_px * max_y_reached
        efficiency = (total_items_area / roll_area * 100) if roll_area > 0 else 0

        nesting_data = {
            "roll_width_px": self.roll_width_px,
            "roll_height_px": max_y_reached,
            "dpi": self.dpi,
            "efficiency_pct": round(efficiency, 2),
            "items": []
        }
        
        # Map items to JSON
        raw_files = os.listdir(os.path.join(self.base_dir, "RAW"))
        for item in images:
            clean_name = item['name'].replace('_prime.tiff', '')
            folder_id = "_".join(item['name'].split("_")[:2])
            db_info = orders_db.get(folder_id, {"id": 0, "qty": 1, "order_id": "N/A", "status": "pending"})
            
            # Find associated preview in RAW
            preview_file = ""
            for rf in raw_files:
                if rf.startswith(folder_id) and ("thumb" in rf.lower() or "preview" in rf.lower()):
                    preview_file = rf
                    break

            nesting_data["items"].append({
                "id": db_info.get("id", 0),
                "name": clean_name,
                "preview": preview_file,
                "order_id": item['order_id'],
                "status": db_info["status"],
                "x": item['x'],
                "y": item['y'],
                "w": item['w'],
                "h": item['h']
            })
            
        import json
        with open(os.path.join(self.ready_dir, "nesting_data.json"), "w") as f:
            json.dump(nesting_data, f, indent=2)

        print(f"NESTING COMPLETE. Final Roll Size: {final_roll.width}x{final_roll.height} px")
        print(f"Data exported to nesting_data.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--margin", type=float, default=5, help="Margin in mm")
    args = parser.parse_args()
    
    # Convert mm to inches for the engine
    margin_cm = args.margin / 10.0
    
    nester = NexusNestingEngine()
    # Override margin based on CLI arg
    nester.margin_px = int((margin_cm / 2.54) * nester.dpi)
    
    nester.run_nesting()
