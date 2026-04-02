from libs.gmail import send_email

if __name__ == '__main__':
    print("Initializing Gmail Delivery Setup for Printivo...")
    print("Step 1: Authorization required for Sending Emails.")
    # I'll just trigger the creds check first
    from libs.gmail import get_google_creds
    get_google_creds()
    print("Success! Gmail scope is now included.")
