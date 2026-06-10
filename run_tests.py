import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(root, "tests")
    passed = 0
    failed = 0

    for filename in sorted(os.listdir(tests_dir)):
        if not filename.endswith(".sc"):
            continue
        sc_path = os.path.join(tests_dir, filename)
        expected_path = sc_path[:-3] + ".expected"
        if not os.path.exists(expected_path):
            print(f"[SKIP] {filename}: no .expected file")
            continue

        result = subprocess.run(
            [sys.executable, os.path.join(root, "main.py"), sc_path],
            text=True,
            capture_output=True,
        )
        actual = result.stdout.replace("\r\n", "\n").strip()
        with open(expected_path, "r", encoding="utf-8") as f:
            expected = f.read().replace("\r\n", "\n").strip()

        if actual == expected:
            print(f"[PASS] {filename}")
            passed += 1
        else:
            print(f"[FAIL] {filename}")
            print("----- expected -----")
            print(expected)
            print("----- actual -------")
            print(actual)
            failed += 1

    print(f"\nResult: {passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
