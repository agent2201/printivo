import os
import sys
import subprocess
import time
import signal

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

TARGET_SCRIPT = os.path.join(ROOT_DIR, 'libs', 'gmail_responder.py')

def run_service():
    print(f"[NEXUS ORCHESTRATOR] Starting Gmail Responder: {TARGET_SCRIPT}")
    
    while True:
        try:
            # Run the responder as a subprocess
            process = subprocess.Popen(
                [sys.executable, TARGET_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                cwd=ROOT_DIR
            )
            
            # Print output in real-time
            for line in process.stdout:
                print(f"[RESPONDER] {line.strip()}")
                
            process.wait()
            
            exit_code = process.returncode
            if exit_code == 0:
                print("[NEXUS ORCHESTRATOR] Responder stopped gracefully. Restarting in 5s...")
            else:
                print(f"[NEXUS ORCHESTRATOR] Responder CRASHED (code {exit_code}). Restarting in 10s...")
                
            time.sleep(5 if exit_code == 0 else 10)
            
        except Exception as e:
            print(f"[NEXUS ORCHESTRATOR] Orchestrator ERROR: {e}")
            time.sleep(30) # Backup delay

if __name__ == '__main__':
    # Force UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Register signal handlers for clean exit
    def stop_handler(signum, frame):
        print("[NEXUS ORCHESTRATOR] Stopping service manager...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    run_service()
