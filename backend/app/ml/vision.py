# app/ml/vision.py
import cv2
import os
import glob

# Initialize ORB detector and BFMatcher
_orb = cv2.ORB_create(nfeatures=1500)
_bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def orb_similarity(img_a_path: str, img_b_path: str) -> float:
    """
    Calculates similarity between two images using ORB keypoint matching.
    Returns a float between 0.0 and 1.0.
    """
    a = cv2.imread(img_a_path, cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(img_b_path, cv2.IMREAD_GRAYSCALE)
    
    if a is None or b is None:
        return 0.0
        
    ka, da = _orb.detectAndCompute(a, None)
    kb, db = _orb.detectAndCompute(b, None)
    
    if da is None or db is None:
        return 0.0
        
    # Match descriptors
    matches = _bf.match(da, db)
    # Keep only good matches (distance < 40)
    good_matches = [m for m in matches if m.distance < 40]
    
    # 150 good matches usually means near-identical layout
    return min(1.0, len(good_matches) / 150.0)

def vision_check(screenshot_path: str, page_domain: str, has_password_form: bool, brands_dir: str = "data/brands") -> dict:
    """
    Compares a screenshot against all reference images in data/brands/<brand>/
    """
    best = {"brand": None, "similarity": 0.0, "matched_image": None}
    
    if not os.path.exists(brands_dir):
        return {"error": f"Brands directory {brands_dir} not found."}

    # Loop through each brand folder (e.g., data/brands/acmepay/)
    for brand_dir in glob.glob(os.path.join(brands_dir, "*")):
        if not os.path.isdir(brand_dir):
            continue
            
        brand_name = os.path.basename(brand_dir)
        
        # Check against all reference images for this brand
        for ref_img in glob.glob(os.path.join(brand_dir, "*.*")):
            if ref_img.lower().endswith(('.png', '.jpg', '.jpeg')):
                sim = orb_similarity(screenshot_path, ref_img)
                if sim > best["similarity"]:
                    best = {"brand": brand_name, "similarity": sim, "matched_image": ref_img}

    # Is the page hosted on the brand's actual official domain?
    owned = False
    if best["brand"]:
        owned = page_domain.endswith(best["brand"])
        
    # High similarity + NOT owned by brand + has a password field = Impersonation
    impersonation = bool(best["similarity"] >= 0.80 and not owned and has_password_form)

    return {
        "best_brand_match": best["brand"],
        "similarity": best["similarity"],
        "matched_reference_image": best["matched_image"],
        "page_domain": page_domain,
        "looks_like_login": has_password_form,
        "impersonation": impersonation
    }