# check_step14.py
import os
import cv2
import numpy as np
from app.ml.vision import vision_check

print("=== STEP 14 VERIFICATION ===\n")

# 1. Setup directories and dummy images for testing
os.makedirs("data/brands/acmepay", exist_ok=True)
os.makedirs("artifacts/test", exist_ok=True)

# Create a fake "AcmePay" login page image (Blue background, white text)
real_img = np.zeros((400, 600, 3), dtype=np.uint8)
real_img[:] = (200, 100, 50) # BGR color (Blueish)
cv2.putText(real_img, "AcmePay", (200, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
cv2.putText(real_img, "Username", (200, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(real_img, "Password", (200, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
real_img_path = "data/brands/acmepay/real_login.png"
cv2.imwrite(real_img_path, real_img)

# Create a "Suspicious Site" image (Copy of the real one, but slightly modified)
fake_img = real_img.copy()
# Change the background slightly to simulate a clone
fake_img[:] = (190, 95, 45)
cv2.putText(fake_img, "AcmePay", (200, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
# Add a fake element
cv2.putText(fake_img, "Verify Account", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
fake_img_path = "artifacts/test/fake_screenshot.png"
cv2.imwrite(fake_img_path, fake_img)

print(f"Created reference image at: {real_img_path}")
print(f"Created test screenshot at: {fake_img_path}\n")

# 2. Run the vision check
# We simulate a page with a password form on a malicious domain
result = vision_check(
    screenshot_path=fake_img_path,
    page_domain="acmepay-secure-login.com",
    has_password_form=True
)

print("--- Vision Check Result ---")
import json
print(json.dumps(result, indent=2))

# 3. Verify logic
if result["impersonation"] and result["similarity"] >= 0.80:
    print("\n✅ SUCCESS: The vision module correctly identified brand impersonation.")
else:
    print("\n❌ FAILED: The vision module did not detect the impersonation.")

print("\n=== DONE ===")