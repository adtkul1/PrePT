#!/usr/bin/env python3
"""
Quick Test Runner - Fast way to test DocGen
Run: python quick_test.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}")
    print(f"$ {cmd}\n")
    
    # Set PYTHONPATH to include src directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path(__file__).parent / "src")
    
    result = subprocess.run(cmd, shell=True, env=env)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED")
    else:
        print(f"\n❌ {description} - FAILED")
    
    return result.returncode == 0


def main():
    """Run quick tests"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║        DocGen - Quick Test Suite                             ║
    ║        Testing the presentation generation system            ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Test 1: CLI Help
    results['CLI Help'] = run_command(
        'python main.py --help',
        'Test 1: CLI Help (No API required)'
    )
    
    # Test 2: List Templates
    results['List Templates'] = run_command(
        'python main.py templates',
        'Test 2: List Templates (No API required)'
    )
    
    # Test 3: Configuration
    results['Configuration'] = run_command(
        'python -c "import sys; sys.path.insert(0, \'src\'); from config import CONFIG, TEMPLATES_DIR; print(f\'Templates: {TEMPLATES_DIR}\')"',
        'Test 3: Configuration Loading (No API required)'
    )
    
    # Test 4: Model Validation
    results['Models'] = run_command(
        'python -c "import sys; sys.path.insert(0, \'src\'); from models import SlideType, SlideOutline; s = SlideOutline(slide_number=1, title=\'Test\', content=[\'point\'], slide_type=SlideType.CONTENT_SLIDE); print(\'✓ Models valid\')"',
        'Test 4: Model Validation (No API required)'
    )
    
    # Test 5: Template Manager
    results['Templates'] = run_command(
        'python -c "import sys; sys.path.insert(0, \'src\'); from template_manager import TemplateManager; tm = TemplateManager(); templates = tm.get_available_templates(); print(f\'Found {len(templates)} templates\')"',
        'Test 5: Template Manager (No API required)'
    )
    
    # Test 6: Unit Tests (skip API tests)
    os.environ['SKIP_API_TESTS'] = '1'
    results['Unit Tests'] = run_command(
        'pytest tests/test_suite.py -v --tb=short -x',
        'Test 6: Unit Tests (No API required)'
    )
    
    # Test 7: Generation (if API key exists)
    if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY'].startswith('sk-'):
        results['Generation'] = run_command(
            'python main.py generate --topic "Python Programming" --slides 4',
            'Test 7: Full Generation (Requires valid API key)'
        )
    else:
        print(f"\n{'='*70}")
        print("⏭️  Test 7: Full Generation - SKIPPED (No valid OpenAI API key)")
        print(f"{'='*70}")
        print("To enable this test, add OPENAI_API_KEY to .env")
        results['Generation'] = None
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result is True else ("❌ FAILED" if result is False else "⏭️  SKIPPED")
        print(f"{test_name:.<40} {status}")
    
    print(f"{'='*70}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print(f"{'='*70}\n")
    
    if failed > 0:
        print("❌ Some tests failed. Check output above for details.")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
