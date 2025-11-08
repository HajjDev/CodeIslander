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
            # --- We run the user's code first in all test types ---
            spec.loader.exec_module(user_module)
            
            # --- TYPE 1: FUNCTION CALL ---
            if case['type'] == 'function_call':
                func_to_test = getattr(user_module, config['function_to_test'])
                actual_output = func_to_test(*case['inputs'])
                expected_output = case['expected_output']

                if str(actual_output) == str(expected_output):
                    test_result['passed'] = True
                
                test_result['actual'] = str(actual_output)
                test_result['expected'] = str(expected_output)
            
            # --- TYPE 2: STDIN / STDOUT ---
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

            # --- NEW: TYPE 3: VARIABLE CHECK ---
            elif case['type'] == 'variable_check':
                expected_vars = json.loads(case['expected_output'])
                failed_checks = []
                all_passed = True

                for var_name, checks in expected_vars.items():
                    try:
                        actual_value = getattr(user_module, var_name)
                        expected_value = checks['value']
                        expected_type_str = checks['type']
                        
                        actual_type_str = type(actual_value).__name__
                        if actual_type_str != expected_type_str:
                            all_passed = False
                            failed_checks.append(f"Variable '{var_name}': Expected type {expected_type_str}, but got {actual_type_str}")
                            continue
                        
                        if actual_value != expected_value:
                            all_passed = False
                            failed_checks.append(f"Variable '{var_name}': Expected value {repr(expected_value)}, but got {repr(actual_value)}")

                    except AttributeError:
                        all_passed = False
                        failed_checks.append(f"Variable '{var_name}' was not defined.")
                    except Exception as e:
                        all_passed = False
                        failed_checks.append(f"Error checking '{var_name}': {e}")
                
                test_result['passed'] = all_passed
                if not all_passed:
                    test_result['actual'] = "\n".join(failed_checks)
                    test_result['expected'] = "All variables to be correctly converted"
                else:
                    test_all_passed = "All variables passed!"
                    test_result['actual'] = test_all_passed
                    test_result['expected'] = test_all_passed

            # --- THIS BLOCK CATCHES THE TYPO ---
            else:
                test_result['passed'] = False
                # Use repr() to show invisible characters (like spaces)
                test_result['actual'] = f"Unknown test type: {repr(case['type'])}"
                test_result['expected'] = "Must be 'function_call', 'stdin_stdout', or 'variable_check'"
            # --- END OF NEW BLOCK ---


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