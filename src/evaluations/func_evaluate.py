from typing import *
import contextlib
import signal
import subprocess
from .executor_utils import function_with_timeout
import sys

def evaluate_io(
    sample_io: list[str],
    completion: str,
    timeout: int = 5,
    stop_early: bool = False,
):
    test_log = ""
    passed = True
    for io in sample_io:
        try:
            code = ("from typing import *\n" if "from typing import *" not in completion else "") + \
                completion + "\n" + io + "\n"
            function_with_timeout(
                exec,
                (code, globals()),
                timeout
            )
            test_log += f"passed in test case: {io}\n"
        except Exception as e:
            if stop_early:
                return False, f"failed in test case: {io}\n"
            passed = False
            test_log += f"failed in test case: {io}\n"

    return passed, test_log


def evaluate_io_et(
    sample_io: list[str],
    completion: str,
    timeout: int = 5,
    prompt: str = "",
):
    io = "\n".join(sample_io)
    try:
        code = ("from typing import *\n" if "from typing import *" not in completion else "") + \
            prompt + completion + "\n" + io + "\n"
        function_with_timeout(
            exec,
            (code, globals()),
            timeout
        )
        return True
    except Exception as e:
        return False


def evaluate_functional_correctness(
    problem: Dict,
    completion: str,
    timeout: int = 5,
    test_key: str = "test",
):
    # if problem["name"] == "mbpp_61_count_Substrings":
    #     pass
    try:
        code = ("from typing import *\n" if "from typing import *" not in completion else "") + \
            completion + "\n" + problem[test_key] + \
            "\n" + f"check({problem['entry_point']})"

        function_with_timeout(
            exec,
            (code, globals()),
            timeout
        )
        return "passed"
    except Exception as e:
        return f"failed: {e}"


def evaluate_functional_correctness2(
    problem: Dict,
    completion: str,
    timeout: float = 10,
) -> Dict:

    check_program = (
        # problem["prompt"] +
        "from typing import *\n" +
        completion + "\n" +
        problem["test"] + "\n" +
        f"check({problem['entry_point']})"
    )
    # print(check_program)

    try:
        exec(check_program)
        return "passed"
    except TimeoutException:
        return "timed out"
    except BaseException as e:
        return f"failed: {e}"


def run_generated_code(generated_code: str, test_cases_code: str, timeout: int = 30) -> Tuple[bool, str]:
    try:
        full_code = f"""
import sys
{generated_code}

{test_cases_code}

if __name__ == "__main__":
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w') if sys.platform != 'win32' else open('nul', 'w'))
    result = runner.run(suite)

    print(f"Tests run: {{result.testsRun}}")
    print(f"Failures: {{len(result.failures)}}")
    print(f"Errors: {{len(result.errors)}}")
    print(f"Success: {{result.testsRun - len(result.failures) - len(result.errors)}}")

    exit(0 if result.wasSuccessful() else 1)
"""

        # 执行测试
        result = subprocess.run(
            [sys.executable, "-c", full_code],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # 解析结果
        output_lines = result.stdout.split('\n')
        success_line = next((line for line in output_lines if 'Success:' in line), None)

        if result.returncode == 0:
            test_log = f"All tests passed!\\n{result.stdout}"
            return "passed", test_log
        else:
            test_log = f"Some tests failed:\\n{result.stdout}\\nErrors:\\n{result.stderr}"
            return False, test_log

    except subprocess.TimeoutExpired:
        return False, "Test execution timed out"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def run_unittest_style_code(generated_code: str, test_cases_code: str, timeout: int = 30) -> Tuple[bool, str]:
    try:

        full_code = f"""
import sys
{generated_code}

{test_cases_code}

if __name__ == "__main__":
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w') if sys.platform != 'win32' else open('nul', 'w'))
    result = runner.run(suite)

    print(f"Tests run: {{result.testsRun}}")
    print(f"Failures: {{len(result.failures)}}")
    print(f"Errors: {{len(result.errors)}}")
    print(f"Success: {{result.testsRun - len(result.failures) - len(result.errors)}}")

    exit(0 if result.wasSuccessful() else 1)
"""

        result = subprocess.run(
            [sys.executable, "-c", full_code],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output_lines = result.stdout.split('\n')
        success_line = next((line for line in output_lines if 'Success:' in line), None)

        if result.returncode == 0:
            test_log = f"All tests passed!\\n{result.stdout}"
            return "passed"
        else:
            test_log = f"Some tests failed:\\n{result.stdout}\\nErrors:\\n{result.stderr}"
            return False

    except subprocess.TimeoutExpired:
        return False, "Test execution timed out"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

class TimeoutException(Exception):
    pass
