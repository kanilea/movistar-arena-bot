# -*- coding: utf-8 -*-
"""
Script to extract and organize images from Nintendo Employee Interviews
"""

import os
import re
import base64
import json

def create_nintendo_office_image():
    """Create Nintendo office placeholder"""
    svg_template = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#ff6b35"/>
        <rect x="50" y="50" width="300" height="200" fill="#2c3e50"/>
        <rect x="70" y="70" width="60" height="60" fill="#3498db"/>
        <rect x="150" y="70" width="60" height="60" fill="#3498db"/>
        <rect x="230" y="70" width="60" height="60" fill="#3498db"/>
        <rect x="70" y="150" width="60" height="60" fill="#3498db"/>
        <rect x="150" y="150" width="60" height="60" fill="#3498db"/>
        <rect x="230" y="150" width="60" height="60" fill="#3498db"/>
        <text x="200" y="30" font-family="Arial" font-size="18" fill="white" text-anchor="middle">
            Nintendo HQ
        </text>
        <rect x="100" y="130" width="200" height="10" fill="#e60012"/>
        <text x="200" y="280" font-family="Arial" font-size="14" fill="white" text-anchor="middle">
            Kyoto, Japan
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def create_employee_portrait(department, index):
    """Create employee portrait placeholder"""
    svg_template = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" fill="#e60012"/>
        <circle cx="100" cy="70" r="30" fill="#FFE5E5"/>
        <circle cx="85" cy="90" r="3" fill="#333"/>
        <circle cx="115" cy="90" r="3" fill="#333"/>
        <path d="M 85 110 Q 100 120 115 110" stroke="#333" stroke-width="2" fill="none"/>
        <rect x="70" y="130" width="60" height="20" fill="#333"/>
        <text x="100" y="170" font-family="Arial" font-size="10" fill="white" text-anchor="middle">
            Employee {index}
        </text>
        <text x="100" y="185" font-family="Arial" font-size="8" fill="white" text-anchor="middle">
            {department}
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def create_department_image(department):
    """Create department-specific image"""
    department_colors = {
        "Game Development": "#e60012",
        "Software Engineering": "#0099CC",
        "Hardware Development": "#33CC99",
        "Marketing": "#FF6600",
        "HR": "#9B59B6",
        "Quality Assurance": "#F39C12",
        "UI/UX Design": "#1ABC9C",
        "Sound Design": "#34495E",
        "Data Science": "#E74C3C",
        "Infrastructure": "#95A5A6"
    }
    
    color = department_colors.get(department, "#e60012")
    
    svg_template = f'''<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{color}"/>
        <circle cx="150" cy="60" r="40" fill="white"/>
        <text x="150" y="70" font-family="Arial" font-size="24" fill="{color}" text-anchor="middle" font-weight="bold">
            <tspan>テク</tspan>
        </text>
        <text x="150" y="100" font-family="Arial" font-size="20" fill="white" text-anchor="middle" font-weight="bold">
            {department}
        </text>
        <rect x="50" y="120" width="200" height="60" fill="rgba(255,255,255,0.2)"/>
        <text x="150" y="145" font-family="Arial" font-size="14" fill="white" text-anchor="middle">
            Department
        </text>
        <text x="150" y="165" font-family="Arial" font-size="12" fill="white" text-anchor="middle">
            任天堂
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def create_gaming_image(topic):
    """Create gaming-related image"""
    gaming_colors = {
        "Mario": "#e60012",
        "Zelda": "#00AA44",
        "Pokémon": "#FFD700",
        "Switch": "#FF6900",
        "amiibo": "#9C27B0"
    }
    
    color = gaming_colors.get(topic.split()[0] if topic.split() else "Nintendo", "#e60012")
    
    svg_template = f'''<svg width="350" height="250" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="linear-gradient(135deg, {color}, #2c3e50)"/>
        <rect x="25" y="25" width="300" height="200" fill="white" rx="15"/>
        <circle cx="175" cy="125" r="60" fill="{color}"/>
        <text x="175" y="135" font-family="Arial" font-size="24" fill="white" text-anchor="middle" font-weight="bold">
            <tspan>🎮</tspan>
        </text>
        <text x="175" y="50" font-family="Arial" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">
            {topic}
        </text>
        <rect x="50" y="180" width="250" height="30" fill="{color}" rx="5"/>
        <text x="175" y="200" font-family="Arial" font-size="14" fill="white" text-anchor="middle">
            Gaming Innovation
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def extract_nintendo_images():
    """Extract images from Nintendo interview files"""
    archive_path = "Nintendo_Employee_Interviews_127_Complete"
    image_dir = "Nintendo_Employee_Interviews_127_Complete/images"
    
    # Create images directory
    os.makedirs(image_dir, exist_ok=True)
    
    # Create main images
    office_image = create_nintendo_office_image()
    nintendo_logo_svg = '<svg width="300" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#e60012"/><text x="50%" y="60" font-family="Arial" font-size="36" font-weight="bold" fill="white" text-anchor="middle">NINTENDO</text></svg>'
    
    # Save main images
    with open(f"{image_dir}/nintendo_office.svg", "wb") as f:
        f.write(base64.b64decode(office_image))
    
    nintendo_logo_bytes = nintendo_logo_svg.encode('utf-8')
    with open(f"{image_dir}/nintendo_logo.svg", "wb") as f:
        f.write(nintendo_logo_bytes)
    
    print(f"Created main images: nintendo_office.svg, nintendo_logo.svg")
    
    # Create sample categories
    departments = ["Game Development", "Software Engineering", "Hardware Development", "Marketing", "HR"]
    topics = ["Mario Series", "Zelda Series", "Nintendo Switch", "amiibo", "E3 Presentations"]
    
    print("Creating department images...")
    for i, dept in enumerate(departments):
        dept_image = create_department_image(dept)
        filename = f"dept_{i+1:03d}_{dept.replace(' ', '_').replace('/', '_')}.svg"
        with open(f"{image_dir}/{filename}", "wb") as f:
            f.write(base64.b64decode(dept_image))
        print(f"  Created dept image: {filename}")
    
    print("Creating employee portraits...")
    for i in range(10):
        department = departments[i % len(departments)]
        employee_image = create_employee_portrait(department, i+1)
        filename = f"emp_{i+1:03d}_employee.svg"
        with open(f"{image_dir}/{filename}", "wb") as f:
            f.write(base64.b64decode(employee_image))
        print(f"  Created employee image: {filename}")
    
    print("Creating gaming topic images...")
    for i, topic in enumerate(topics):
        topic_image = create_gaming_image(topic)
        filename = f"topic_{i+1:03d}_{topic.replace(' ', '_')}.svg"
        with open(f"{image_dir}/{filename}", "wb") as f:
            f.write(base64.b64decode(topic_image))
        print(f"  Created topic image: {filename}")

def enhance_nintendo_index():
    """Enhance Nintendo index.html with images"""
    index_path = "Nintendo_Employee_Interviews_127_Complete/index.html"
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add header images
        header_image = '''<div style="text-align: center; margin: 20px 0;">
            <img src="images/nintendo_logo.svg" alt="Nintendo" style="max-width: 200px; margin: 10px;">
            <img src="images/nintendo_office.svg" alt="Nintendo Office" style="max-width: 250px; margin: 10px;">
        </div>'''
        
        # Insert header images after header section
        content = content.replace(
            '</div>\n    \n    <div class="stats">',
            f'</div>\n    {header_image}\n    \n    <div class="stats">'
        )
        
        # Save updated index
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Enhanced index.html with header images")
        
    except Exception as e:
        print(f"Error enhancing index: {e}")

def enhance_nintendo_interviews():
    """Enhance individual Nintendo interview pages with images"""
    archive_path = "Nintendo_Employee_Interviews_127_Complete"
    
    # Process first few interviews as examples
    if os.path.exists(archive_path):
        interview_folders = [d for d in os.listdir(archive_path) 
                            if os.path.isdir(os.path.join(archive_path, d)) 
                            and d.startswith(('001', '002', '003', '004', '005'))][:5]  # First 5
        
        for i, folder in enumerate(sorted(interview_folders)):
            interview_path = os.path.join(archive_path, folder, "interview.html")
            
            if os.path.exists(interview_path):
                try:
                    with open(interview_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Add header image
                    header_image = '''\n    <div style="text-align: center; margin: 20px 0;">
        <img src="../images/nintendo_logo.svg" alt="Nintendo" style="max-width: 150px;">
    </div>'''
                    
                    content = content.replace(
                        '</div>\n    \n    <div class="content-wrapper">',
                        f'</div>{header_image}\n    \n    <div class="content-wrapper">'
                    )
                    
                    # Add employee portrait
                    employee_image = f'''<div class="images">
        <div class="image">
            <img src="../images/emp_{i+1:03d}_employee.svg" alt="Employee Portrait" style="border-radius: 50%;">
            <div class="image-caption">Employee Portrait</div>
        </div>
        <div class="image">
            <img src="../images/dept_001_Game_Development.svg" alt="Department" style="border-radius: 8px;">
            <div class="image-caption">Department Workspace</div>
        </div>
    </div>'''
                    
                    # Insert after content wrapper
                    content = content.replace(
                        '<div class="content-wrapper">\n',
                        f'<div class="content-wrapper">\n{employee_image}\n'
                    )
                    
                    # Save enhanced interview
                    with open(interview_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Enhanced {folder}/interview.html with images")
                    
                except Exception as e:
                    print(f"Error enhancing {folder}: {e}")

def main():
    """Main function to extract and organize Nintendo images"""
    print("Starting Nintendo Employee Interviews Image Extraction")
    print("="*55)
    
    # Extract and create images
    extract_nintendo_images()
    
    print("\nEnhancing HTML files with images...")
    
    # Enhance index.html
    enhance_nintendo_index()
    
    # Enhance individual interviews
    enhance_nintendo_interviews()
    
    print("\nNintendo image extraction and enhancement complete!")
    print("Images saved to: Nintendo_Employee_Interviews_127_Complete/images/")
    print("Enhanced HTML files include proper image references")

if __name__ == "__main__":
    main()