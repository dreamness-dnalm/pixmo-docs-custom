"""
Utility functions for exporting datasets to JSONL format and saving images as PNG files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import pyarrow as pa
from PIL import Image
import io


def arrow_to_jsonl(arrow_file_path: str, jsonl_file_path: str) -> None:
    """
    Convert an Arrow file to JSONL format.
    
    Args:
        arrow_file_path: Path to the input Arrow file
        jsonl_file_path: Path to the output JSONL file
    """
    # Read the Arrow file
    with pa.ipc.open_stream(arrow_file_path) as reader:
        table = reader.read_all()
    
    # Convert to pandas for easier processing
    df = table.to_pandas()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(jsonl_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write to JSONL file
    with open(jsonl_file_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # Convert the row to a dictionary
            row_dict = row.to_dict()
            
            # Handle image data - convert to base64 or remove for JSONL
            if 'image' in row_dict and row_dict['image'] is not None:
                # For JSONL, we'll store the image path instead of the binary data
                if isinstance(row_dict['image'], dict) and 'bytes' in row_dict['image']:
                    row_dict['image_path'] = row_dict['image'].get('path', '')
                    row_dict['image_bytes_size'] = len(row_dict['image'].get('bytes', b''))
                elif hasattr(row_dict['image'], 'get'):
                    row_dict['image_path'] = row_dict['image'].get('path', '')
                    row_dict['image_bytes_size'] = len(row_dict['image'].get('bytes', b''))
                else:
                    row_dict['image_path'] = ''
                    row_dict['image_bytes_size'] = 0
                # Remove the complex image object for JSONL
                del row_dict['image']
            
            # Handle nested JSON strings that might contain Unicode escapes
            for key, value in row_dict.items():
                if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                    try:
                        # Try to parse as JSON and re-serialize with ensure_ascii=False
                        parsed_value = json.loads(value)
                        row_dict[key] = json.dumps(parsed_value, ensure_ascii=False)
                    except (json.JSONDecodeError, TypeError):
                        # If it's not valid JSON, leave it as is
                        pass
            
            # Write as JSON line
            f.write(json.dumps(row_dict, ensure_ascii=False, indent=None) + '\n')


def save_images_from_arrow(arrow_file_path: str, output_dir: str) -> Dict[str, str]:
    """
    Extract and save images from an Arrow file as PNG files.
    
    Args:
        arrow_file_path: Path to the input Arrow file
        output_dir: Directory to save PNG files
        
    Returns:
        Dictionary mapping row indices to saved image paths
    """
    # Read the Arrow file
    with pa.ipc.open_stream(arrow_file_path) as reader:
        table = reader.read_all()
    
    # Convert to pandas for easier processing
    df = table.to_pandas()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    saved_images = {}
    
    for idx, row in df.iterrows():
        if 'image' in row and row['image'] is not None:
            try:
                # Extract image data
                image_bytes = None
                if isinstance(row['image'], dict) and 'bytes' in row['image']:
                    image_bytes = row['image'].get('bytes')
                elif hasattr(row['image'], 'get'):
                    image_bytes = row['image'].get('bytes')
                
                if image_bytes:
                    # Load image from bytes
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Generate filename
                    filename = f"image_{idx:04d}.png"
                    image_path = os.path.join(output_dir, filename)
                    
                    # Save as PNG
                    image.save(image_path, 'PNG')
                    saved_images[str(idx)] = image_path
                    
                    print(f"Saved image {idx} to {image_path}")
                else:
                    print(f"No image bytes found for row {idx}")
            except Exception as e:
                print(f"Error saving image for row {idx}: {e}")
    
    return saved_images


def process_arrow_dataset(arrow_file_path: str, output_base_path: str) -> Dict[str, str]:
    """
    Process an Arrow dataset by converting to JSONL and saving images as PNG.
    
    Args:
        arrow_file_path: Path to the input Arrow file
        output_base_path: Base path for output files (without extensions)
        
    Returns:
        Dictionary with paths to generated files
    """
    results = {}
    
    # Generate output paths
    jsonl_path = f"{output_base_path}.jsonl"
    images_dir = f"{output_base_path}_images"
    
    # Convert to JSONL
    print(f"Converting {arrow_file_path} to JSONL...")
    arrow_to_jsonl(arrow_file_path, jsonl_path)
    results['jsonl'] = jsonl_path
    print(f"JSONL saved to: {jsonl_path}")
    
    # Save images as PNG
    print(f"Extracting images from {arrow_file_path}...")
    saved_images = save_images_from_arrow(arrow_file_path, images_dir)
    results['images_dir'] = images_dir
    results['saved_images'] = saved_images
    print(f"Images saved to: {images_dir}")
    print(f"Saved {len(saved_images)} images")
    
    return results


def process_session_output(session_output_dir: str) -> None:
    """
    Process all Arrow files in the session output directory.
    
    Args:
        session_output_dir: Path to the session output directory
    """
    session_path = Path(session_output_dir)
    
    if not session_path.exists():
        print(f"Session output directory {session_output_dir} does not exist")
        return
    
    # Find all Arrow files recursively
    arrow_files = list(session_path.rglob("*.arrow"))
    
    if not arrow_files:
        print(f"No Arrow files found in {session_output_dir}")
        return
    
    print(f"Found {len(arrow_files)} Arrow files to process")
    
    for arrow_file in arrow_files:
        print(f"\nProcessing: {arrow_file}")
        
        # Generate output base path (same as arrow file but without extension)
        output_base = str(arrow_file.with_suffix(''))
        
        try:
            results = process_arrow_dataset(str(arrow_file), output_base)
            print(f"✓ Successfully processed {arrow_file.name}")
        except Exception as e:
            print(f"✗ Error processing {arrow_file.name}: {e}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        session_dir = sys.argv[1]
    else:
        session_dir = "./session_output"
    
    process_session_output(session_dir)
