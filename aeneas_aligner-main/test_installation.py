#!/usr/bin/env python3
"""
Test script to verify all dependencies are properly installed
Run this script to check if your system is ready for the audio-text aligner
"""

import sys
import subprocess

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.7+")
        return False

def test_system_dependencies():
    """Test system dependencies (espeak, ffmpeg)"""
    print("\n🔧 Testing system dependencies...")
    
    # Test espeak
    try:
        result = subprocess.run(['espeak', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ espeak - OK")
            espeak_ok = True
        else:
            print("❌ espeak - Not working")
            espeak_ok = False
    except FileNotFoundError:
        print("❌ espeak - Not installed")
        espeak_ok = False
    except Exception as e:
        print(f"❌ espeak - Error: {e}")
        espeak_ok = False
    
    # Test ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ ffmpeg - OK")
            ffmpeg_ok = True
        else:
            print("❌ ffmpeg - Not working")
            ffmpeg_ok = False
    except FileNotFoundError:
        print("❌ ffmpeg - Not installed")
        ffmpeg_ok = False
    except Exception as e:
        print(f"❌ ffmpeg - Error: {e}")
        ffmpeg_ok = False
    
    return espeak_ok and ffmpeg_ok

def test_python_packages():
    """Test Python packages"""
    print("\n📦 Testing Python packages...")
    
    packages = {
        'aeneas': 'aeneas.executetask',
        'gradio': 'gradio',
        'pdfminer.six': 'pdfminer.high_level',
        'python-docx': 'docx'
    }
    
    all_ok = True
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} - OK")
        except ImportError:
            print(f"❌ {package_name} - Not installed")
            all_ok = False
        except Exception as e:
            print(f"❌ {package_name} - Error: {e}")
            all_ok = False
    
    return all_ok

def test_aeneas_functionality():
    """Test aeneas basic functionality"""
    print("\n🎯 Testing aeneas functionality...")
    
    try:
        from aeneas.executetask import ExecuteTask
        from aeneas.task import Task
        print("✅ aeneas imports - OK")
        
        # Test basic task creation
        config = "task_language=eng|is_text_type=plain|os_task_file_format=srt"
        task = Task(config_string=config)
        print("✅ aeneas task creation - OK")
        
        return True
    except Exception as e:
        print(f"❌ aeneas functionality - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Audio-Text Aligner - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("System Dependencies", test_system_dependencies),
        ("Python Packages", test_python_packages),
        ("Aeneas Functionality", test_aeneas_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready for audio-text alignment.")
        print("Run 'python app.py' to start the application.")
    else:
        print("\n⚠️  Some tests failed. Please install missing dependencies:")
        print("1. System dependencies: sudo apt-get install espeak ffmpeg")
        print("2. Python packages: pip install -r requirements.txt")
        print("3. For Windows: Download espeak and ffmpeg manually")

if __name__ == "__main__":
    main() 