# run_tests.py
import importlib.util
import json
import sys
import io
from contextlib import redirect_stdout

def run_all_tests(user_code_path):
    results = []
    
    try:
        config_data = sys.stdin.read()
        config = json.loads(config_data)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to read test config from stdin: {e}"}))
        sys.exit(1)

    try:
        spec = importlib.util.spec_from_file_location(config['module_name'], user_code_path)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to import code: {e}"}))
        sys.exit(1)

    for case in config['test_cases']:
        is_hidden = case.get('is_hidden', False)
        test_result = {
            "name": case['name'],
            "passed": False,
            "actual": "",
            "expected": "",
            "is_hidden": is_hidden
        }
        
        try:
            if case['type'] == 'function_call':
                func_to_test = getattr(user_module, config['function_to_test'])
                actual_output = func_to_test(*case['inputs'])
                expected_output = case['expected_output']

                if str(actual_output) == str(expected_output):
                    test_result['passed'] = True
                
                test_result['actual'] = str(actual_output)
                test_result['expected'] = str(expected_output)

            elif case['type'] == 'stdin_stdout':
                sys.stdin = io.StringIO(case['stdin'])
                f = io.StringIO()
                with redirect_stdout(f):
                    spec.loader.exec_module(user_module)
                
                actual_output = f.getvalue()
                expected_output = case['expected_output']

                if actual_output == expected_output:
                    test_result['passed'] = True
                
                test_result['actual'] = actual_output
                test_result['expected'] = expected_output

            if not test_result['passed'] and is_hidden:
                test_result['actual'] = "[Hidden]"
                test_result['expected'] = "[Hidden]"

        except Exception as e:
            test_result['actual'] = f"Error: {e}"
            if is_hidden:
                test_result['expected'] = "[Hidden]"
        
        results.append(test_result)

    print(json.dumps({"status": "completed", "results": results}))

if __name__ == "__main__":
    USER_CODE_FILE = '/app/user_code.py'
    run_all_tests(USER_CODE_FILE)