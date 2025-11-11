# run_tests.py
import importlib.util
import json
import sys
import io
import os
import traceback 
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
        # --- 1. Load setup.py (if it exists) and execute it ---
        setup_file_path = '/app/setup.py'
        setup_module = None
        if os.path.exists(setup_file_path):
            setup_spec = importlib.util.spec_from_file_location('setup', setup_file_path)
            setup_module = importlib.util.module_from_spec(setup_spec)
            setup_spec.loader.exec_module(setup_module) 

        # --- 2. Load user_code.py (but don't run it yet) ---
        user_spec = importlib.util.spec_from_file_location(config['module_name'], user_code_path)
        user_module = importlib.util.module_from_spec(user_spec)

        # --- 3. Inject setup variables into user_module ---
        if setup_module:
            for name, value in setup_module.__dict__.items():
                if not name.startswith('__'):
                    setattr(user_module, name, value)
    
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to import code: {traceback.format_exc()}"}))
        sys.exit(1)

    for case in config['test_cases']:
        is_hidden = case.get('is_hidden', False)
        test_result = {"name": case['name'], "passed": False, "actual": "", "expected": "", "is_hidden": is_hidden}
        
        try:
            # --- 4. EXECUTION IS NOW MOVED *INSIDE* EACH TEST TYPE ---
            # This prevents print() statements from polluting the final JSON.
            
            # --- TYPE 1: FUNCTION CALL ---
            if case['type'] == 'function_call':
                user_spec.loader.exec_module(user_module) # Run module
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
                    user_spec.loader.exec_module(user_module) # Run module
                
                actual_output = f.getvalue()
                expected_output = case['expected_output']

                if actual_output == expected_output:
                    test_result['passed'] = True
                
                test_result['actual'] = actual_output
                test_result['expected'] = expected_output

            # --- TYPE 3: VARIABLE CHECK (with Class support) ---
            elif case['type'] == 'variable_check':
                user_spec.loader.exec_module(user_module) # Run module
                expected_vars = json.loads(case['expected_output'])
                failed_checks = []
                all_passed = True
                for var_name, checks in expected_vars.items():
                    try:
                        actual_value = getattr(user_module, var_name)
                        expected_type_str = checks['type']
                        actual_type_str = type(actual_value).__name__
                        if actual_type_str != expected_type_str:
                            all_passed = False
                            failed_checks.append(f"Variable '{var_name}': Expected type {expected_type_str}, but got {actual_type_str}")
                            continue
                        
                        if 'attributes' in checks:
                            for attr_name, attr_checks in checks['attributes'].items():
                                try:
                                    attr_val = getattr(actual_value, attr_name)
                                    exp_attr_val = attr_checks['value']
                                    exp_attr_type = attr_checks['type']
                                    actual_attr_type = type(attr_val).__name__
                                    if actual_attr_type != exp_attr_type:
                                        all_passed = False
                                        failed_checks.append(f"Attribute '{var_name}.{attr_name}': Expected type {exp_attr_type}, but got {actual_attr_type}")
                                    elif attr_val != exp_attr_val:
                                        all_passed = False
                                        failed_checks.append(f"Attribute '{var_name}.{attr_name}': Expected value {repr(exp_attr_val)}, but got {repr(attr_val)}")
                                except AttributeError:
                                    all_passed = False
                                    failed_checks.append(f"Attribute '{var_name}.{attr_name}' was not defined.")
                                except Exception as e:
                                    all_passed = False
                                    failed_checks.append(f"Error checking '{var_name}.{attr_name}': {e}")
                        
                        elif 'value' in checks:
                            expected_value = checks['value']
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
                    test_result['expected'] = "All variables and attributes to be correct"
                else:
                    test_result['actual'] = "All checks passed!"
                    test_result['expected'] = "All checks passed!"

            # --- TYPE 4: FILE CHECK ---
            elif case['type'] == 'file_check':
                user_spec.loader.exec_module(user_module) # Run module
                expected_files = json.loads(case['expected_output'])
                if not isinstance(expected_files, list):
                    expected_files = [expected_files]
                failed_checks = []
                all_passed = True
                for expected_file in expected_files:
                    file_name = expected_file['file_name']
                    expected_content = expected_file['content']
                    file_path_in_container = f'/app/{file_name}'
                    try:
                        if not os.path.exists(file_path_in_container):
                            all_passed = False
                            failed_checks.append(f"File '{file_name}' was not created.")
                            continue
                        with open(file_path_in_container, 'r') as f:
                            actual_content = f.read()
                        if actual_content != expected_content:
                            all_passed = False
                            failed_checks.append(f"File '{file_name}' content mismatch.")
                            if not is_hidden:
                                test_result['actual'] = actual_content
                                test_result['expected'] = expected_content
                    except Exception as e:
                        all_passed = False
                        failed_checks.append(f"Error reading file '{file_name}': {e}")
                
                test_result['passed'] = all_passed
                if not all_passed:
                    test_result['actual'] = "\n".join(failed_contacts)
                    test_result['expected'] = f"{len(expected_files)} file(s) to be correct."
                else:
                    test_result['actual'] = "All files passed!"
                    test_result['expected'] = "All files passed!"
            
            # --- Debugging 'else' block ---
            else:
                test_result['passed'] = False
                test_result['actual'] = f"Unknown test type: {repr(case['type'])}"
                test_result['expected'] = "Must be 'function_call', 'stdin_stdout', 'variable_check', or 'file_check'"

            if not test_result['passed'] and is_hidden:
                test_result['actual'] = "[Hidden]"
                test_result['expected'] = "[Hidden]"

        except Exception as e:
            # --- 5. UPGRADED ERROR REPORTING ---
            
            tb_lines = traceback.format_exc().splitlines()
            
            clean_traceback = []
            for line in tb_lines:
                if '/app/user_code.py' in line:
                    friendly_line = line.strip().replace('"/app/user_code.py"', '"Your Code"')
                    clean_traceback.append(friendly_line)
            
            clean_traceback.append(tb_lines[-1]) # The error message (e.g., SyntaxError: invalid syntax)
            
            test_result['actual'] = "\n".join(clean_traceback)
            if is_hidden:
                test_result['expected'] = "[Hidden]"
        
        results.append(test_result)

    print(json.dumps({"status": "completed", "results": results}))

if __name__ == "__main__":
    USER_CODE_FILE = '/app/user_code.py'
    run_all_tests(USER_CODE_FILE)