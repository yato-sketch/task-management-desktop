#!/usr/bin/env python3
"""
Create a simple icon for the Task Manager application
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple icon for the application"""
    
    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle background
    margin = 20
    bg_color = (76, 175, 80, 255)  # Green background
    draw.rounded_rectangle(
        [margin, margin, size-margin, size-margin],
        radius=30,
        fill=bg_color
    )
    
    # Draw a checkmark (task completion symbol)
    check_color = (255, 255, 255, 255)  # White
    check_thickness = 15
    
    # Checkmark coordinates
    check_points = [
        (size*0.3, size*0.5),  # Start
        (size*0.45, size*0.65), # Middle
        (size*0.7, size*0.35)   # End
    ]
    
    # Draw the checkmark
    for i in range(len(check_points) - 1):
        start = check_points[i]
        end = check_points[i + 1]
        draw.line([start, end], fill=check_color, width=check_thickness)
    
    # Add a small circle for the dot
    dot_center = (size*0.3, size*0.5)
    dot_radius = 8
    draw.ellipse(
        [dot_center[0] - dot_radius, dot_center[1] - dot_radius,
         dot_center[0] + dot_radius, dot_center[1] + dot_radius],
        fill=check_color
    )
    
    # Save as ICO file
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("✅ Created icon.ico")
    
    # Also save as PNG for reference
    img.save('icon.png', format='PNG')
    print("✅ Created icon.png")

if __name__ == "__main__":
    try:
        create_app_icon()
        print("🎨 Icon creation completed!")
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        print("The build will continue without a custom icon.")
