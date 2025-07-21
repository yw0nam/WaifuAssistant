#!/usr/bin/env python3
"""
Sequential E2E test runner to prevent service overload.
This script runs E2E tests one by one with delays to prevent 500 errors.
"""

import subprocess
import sys
import time

# AIDEV-NOTE: Run E2E tests sequentially to prevent ASR service overload
E2E_TESTS = [
    "services/asr_service/test_asr_service.py::test_asr_service_e2e_real_api",
    "services/asr_service/test_asr_service.py::test_asr_service_e2e_different_languages",
    "services/asr_service/test_asr_service.py::test_asr_service_e2e_error_handling",
    "services/llm_service/test_llm_service.py::test_llm_service_e2e_real_api",
    "services/llm_service/test_llm_service.py::test_llm_service_e2e_with_mcp",
    "services/llm_service/test_llm_service.py::test_llm_service_e2e_error_handling",
    "services/tts_service/test_tts_service.py::test_tts_service_e2e_real_api",
    "services/tts_service/test_tts_service.py::test_tts_service_e2e_with_reference_id",
    "services/tts_service/test_tts_service.py::test_tts_service_e2e_error_handling",
]

DELAY_BETWEEN_TESTS = 2.0  # 2 seconds between tests


def run_test(test_path):
    """Run a single test and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {test_path}")
    print(f"{'='*60}")

    cmd = ["uv", "run", "pytest", test_path, "-v", "-s"]
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running test {test_path}: {e}")
        return False


def main():
    """Run all E2E tests sequentially."""
    print("Starting sequential E2E test execution...")

    passed = []
    failed = []

    for i, test in enumerate(E2E_TESTS):
        print(f"\nProgress: {i+1}/{len(E2E_TESTS)}")

        success = run_test(test)

        if success:
            passed.append(test)
            print(f"✅ PASSED: {test}")
        else:
            failed.append(test)
            print(f"❌ FAILED: {test}")

        # Delay between tests to prevent service overload
        if i < len(E2E_TESTS) - 1:  # Don't delay after the last test
            print(f"Waiting {DELAY_BETWEEN_TESTS} seconds before next test...")
            time.sleep(DELAY_BETWEEN_TESTS)

    # Summary
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")

    if failed:
        print("\nFailed tests:")
        for test in failed:
            print(f"  - {test}")
        sys.exit(1)
    else:
        print("\n🎉 All E2E tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
