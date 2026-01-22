import cv2
import numpy as np


def measure_single_object(image_path, scale_factor=0.1):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to separate object from background
    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    
    # Find contours of the object
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    
    if len(contours) == 0:
        raise ValueError("No contours found in the image")
    
    # Draw contours on the original image
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    
    # Get the area of the largest contour in pixels
    area_pixels = cv2.contourArea(contours[0])
    
    # Convert area from pixels to real-world units (cm²)
    size_cm2 = area_pixels * (scale_factor ** 2)
    
    return size_cm2, img


def measure_multiple_objects(image_path, min_area=100):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Otsu's threshold for better object separation
    ret, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    
    # Find contours of all objects
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    object_sizes = []
    
    # Process each contour
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Filter out very small contours (noise)
        if area < min_area:
            continue
        
        object_sizes.append(area)
        
        # Draw bounding box around each object
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Display area on the image
        cv2.putText(
            img, f"{area:.0f}px", (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
        )
    
    return object_sizes, img


def measure_with_reference(image_path, reference_width_cm, reference_contour_idx=0):
    """
    Measure object size using a reference object of known size.
    
    Args:
        image_path (str): Path to the image file
        reference_width_cm (float): Known width of reference object in cm
        reference_contour_idx (int): Index of the reference object contour
    
    Returns:
        tuple: (dictionary of measurements, processed image)
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    if len(contours) <= reference_contour_idx:
        raise ValueError("Reference contour not found")
    
    # Get the reference object's bounding box
    ref_x, ref_y, ref_w, ref_h = cv2.boundingRect(contours[reference_contour_idx])
    
    # Calculate pixels per centimeter
    pixels_per_cm = ref_w / reference_width_cm
    
    measurements = {}
    
    # Measure all objects
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Convert to real-world measurements
        width_cm = w / pixels_per_cm
        height_cm = h / pixels_per_cm
        area_cm2 = cv2.contourArea(cnt) / (pixels_per_cm ** 2)
        
        measurements[f"object_{i}"] = {
            "width_cm": width_cm,
            "height_cm": height_cm,
            "area_cm2": area_cm2
        }
        
        # Draw on image
        color = (0, 255, 0) if i == reference_contour_idx else (255, 0, 0)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            img, f"{width_cm:.1f}x{height_cm:.1f}cm", (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )
    
    return measurements, img


if __name__ == "__main__":
    sizes, processed_img = measure_multiple_objects('ComputerVision\multiple_objects6.jpg')
    print(f'Found {len(sizes)} objects')
    for i, size in enumerate(sizes):
        print(f'Object {i+1}: {size:.2f} pixels²')
    cv2.imwrite('ComputerVision\multiple_objects_result6.jpg', processed_img)
    
    print("Object size measurement module loaded successfully!")