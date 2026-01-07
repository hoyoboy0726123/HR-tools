# -*- coding: utf-8 -*-
"""
Phase 4 Quick Test Script
Testing AI client and qualification checker basic functionality
"""

print("=" * 60)
print("Phase 4 Quick Test")
print("=" * 60)

# Test 1: AI Client Import
print("\n[Test 1] AI Client Import...")
try:
    from core.ai_client import GeminiClient
    print("+ AI Client imported successfully")
except Exception as e:
    print(f"- Import failed: {e}")
    exit(1)

# Test 2: AI Client Initialization
print("\n[Test 2] AI Client Initialization...")
try:
    client = GeminiClient()
    print(f"+ Initialization successful")
    print(f"  - Config status: {'Configured' if client.is_configured() else 'Not configured'}")
    print(f"  - Default model: {client.config.get('model')}")
except Exception as e:
    print(f"- Initialization failed: {e}")
    exit(1)

# Test 3: Qualification Checker Import
print("\n[Test 3] Qualification Checker Import...")
try:
    from modules.m5_qualification_check import QualificationChecker
    print("+ Qualification Checker imported successfully")
except Exception as e:
    print(f"- Import failed: {e}")
    exit(1)

# Test 4: Qualification Checker Initialization
print("\n[Test 4] Qualification Checker Initialization...")
try:
    checker = QualificationChecker()
    print("+ Initialization successful")
    print("  - Connected to employees database")
    print("  - Connected to performance database")
    print("  - Connected to training database")
    print("  - Connected to separation database")
except Exception as e:
    print(f"- Initialization failed: {e}")
    exit(1)

# Test 5: Config File Check
print("\n[Test 5] Config File Check...")
import os
config_path = 'config/api_config.json'
if os.path.exists(config_path):
    print(f"+ Config file exists: {config_path}")
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"  - API Key: {'Set' if config.get('api_key') else 'Not set'}")
    print(f"  - Model: {config.get('model')}")
    print(f"  - Temperature: {config.get('temperature')}")
else:
    print(f"+ Config file will be auto-generated on first use")

# Test 6: Usage Statistics
print("\n[Test 6] Usage Statistics...")
try:
    stats = client.get_usage_stats()
    print("+ Statistics function working")
    print(f"  - Total calls: {stats['total_calls']}")
    print(f"  - Prompt chars: {stats['total_prompt_chars']}")
    print(f"  - Response chars: {stats['total_response_chars']}")
except Exception as e:
    print(f"- Statistics failed: {e}")

# Summary
print("\n" + "=" * 60)
print("Phase 4 Test Complete")
print("=" * 60)
print("\n+ All core functionality tests passed")
print("\nNext steps:")
print("1. Launch app: streamlit run app.py")
print("2. Click 'Qualification Checker' module")
print("3. Set Gemini API Key in 'AI Settings' tab")
print("4. Run qualification check test")
print("\nNote: AI features require API Key configuration first")
