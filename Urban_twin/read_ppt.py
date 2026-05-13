import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_pptx(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            # Find all slide files
            slide_files = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            
            # Sort slides by number
            def get_slide_num(filename):
                try:
                    num_str = filename.replace('ppt/slides/slide', '').replace('.xml', '')
                    return int(num_str)
                except ValueError:
                    return 0
            
            slide_files.sort(key=get_slide_num)
            
            for slide_file in slide_files:
                print(f"--- {slide_file} ---")
                xml_content = z.read(slide_file)
                root = ET.fromstring(xml_content)
                
                # The text is usually inside <a:t> tags
                namespaces = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
                texts = root.findall('.//a:t', namespaces)
                for t in texts:
                    if t.text:
                        print(t.text)
                print("\n")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    ppt_path = "/home/sharath-irappa/Urban_twin/witch_hunt_project.pptx"
    extract_text_from_pptx(ppt_path)
