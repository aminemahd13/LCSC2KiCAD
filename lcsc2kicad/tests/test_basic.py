"""
Test module for lcsc2kicad converter

Run from command line: python -m lcsc2kicad.tests.test_basic
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lcsc2kicad.api import LCSCApi
from lcsc2kicad.utils import setup_logger


def test_api_connection():
    """Test API connection and data retrieval"""
    print("Testing LCSC API connection...")
    
    setup_logger(logging.INFO)
    api = LCSCApi()
    
    # Test with a common component (100nF capacitor)
    test_id = "C1525"
    print(f"Fetching data for {test_id}...")
    
    data = api.get_cad_data(test_id)
    
    if data:
        print("✓ API connection successful!")
        print(f"  Component: {data.get('title', 'Unknown')}")
        print(f"  LCSC: {data.get('lcsc', 'N/A')}")
        print(f"  Manufacturer: {data.get('manufacturer', 'N/A')}")
        return True
    else:
        print("✗ API connection failed!")
        return False


def test_library_structure():
    """Test library structure creation"""
    print("\nTesting library structure creation...")
    
    from lcsc2kicad.utils import create_library_structure
    
    test_dir = Path("test_output")
    
    try:
        create_library_structure(test_dir)
        
        # Check if directories were created
        checks = [
            test_dir.exists(),
            (test_dir / "lcsc2kicad.pretty").exists(),
            (test_dir / "lcsc2kicad.3dshapes").exists(),
            (test_dir / "lcsc2kicad.kicad_sym").exists(),
        ]
        
        if all(checks):
            print("✓ Library structure created successfully!")
            
            # Clean up
            import shutil
            shutil.rmtree(test_dir)
            
            return True
        else:
            print("✗ Library structure incomplete!")
            return False
            
    except Exception as e:
        print(f"✗ Error creating library structure: {e}")
        return False


def main():
    """Run basic tests"""
    print("=" * 50)
    print("LCSC2KiCAD Basic Tests")
    print("=" * 50)
    
    results = []
    
    # Test API
    results.append(test_api_connection())
    
    # Test library structure
    results.append(test_library_structure())
    
    print("\n" + "=" * 50)
    if all(results):
        print("All tests passed! ✓")
        return 0
    else:
        print(f"Some tests failed ({sum(results)}/{len(results)} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
