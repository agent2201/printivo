import sys
import os

# Add root directory to sys.path to resolve libs.nexus_mailer
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from libs.nexus_mailer import send_templated_email

def test_run():
    print("🚀 Initializing NEXUS Printivo Templated Email Service...")
    
    # Placeholder recipient (usually the user or teammate like Eugene)
    # The user should change this
    recipient = "admin@example.com"  # CHANGE THIS
    
    success = send_templated_email(
        to=recipient,
        subject="NEXUS: New Render Ready (Comp 1_22)",
        title="High-Efficiency Video Ready",
        recipient_name="Eugene",
        message_body=(
            "The new HEVC 444 Alpha render has been successfully processed by the Printivo Engine. "
            "Optimization status: 100%. Quality: Lossless."
        ),
        cta_text="Download Asset",
        cta_link="https://github.com/agent2201/printivo"
    )

    if success:
        print("✅ Success: Templated email sent correctly.")
    else:
        print("❌ Error: Check logs for details.")

if __name__ == "__main__":
    test_run()
