import json
import os
import uuid
import subprocess
import shutil
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ...models import Exercise, Tests 

# --- View to Render the HTML Page ---

@login_required
def exercise_page(request, exercise_id):
    """
    Renders the specific exercise page for a logged-in user.
    """
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    
    if request.user.is_staff:
        perm = True
    else:
        perm = request.user.unlockedExercises.filter(pk=exercise.id).exists()
        
    if not perm:
        return redirect("home") 
        
    prompt = {'exercise': exercise}
    return render(request, "runner.html", prompt)


    
# --- View to Securely Execute Code (BYPASS VERSION) ---

@csrf_exempt
def run_code_secure(request, exercise_id):
    """
    This view runs user code inside a secure Docker container
    using the "bypass" method, as the local python-sandbox image is broken.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    host_temp_dir = None
    
    # !! ================== IMPORTANT ================== !!
    # You MUST set this to the full, absolute path of your run_tests.py file
    # e.g., '/Users/hajj/LearnHowToCode/Backend/run_tests.py'
    #
    # To get it: Right-click run_tests.py in VS Code and choose "Copy Path"
    #
    RUNNER_SCRIPT_PATH = '/Users/hajj/LearnHowToCode/Backend/backend/run_tests.py'
    # !! =============================================== !!

    # Check if the path is valid *before* doing anything else
    if not os.path.exists(RUNNER_SCRIPT_PATH):
        return JsonResponse({
            'status': 'error',
            'message': 'CRITICAL SERVER ERROR: The RUNNER_SCRIPT_PATH in code_runner.py is incorrect. Please contact an admin.'
        }, status=500)

    try:
        # --- 1. Get code and Fetch Exercise ---
        body = json.loads(request.body)
        code = body.get('code', '') 
        if not code:
            return JsonResponse({'error': 'No code provided.'}, status=400)
        
        exercise = get_object_or_404(
            Exercise.objects.prefetch_related('tests'), 
            pk=exercise_id
        )
        # --- ADD THIS DEBUG CODE ---
        print("--- DEBUG: FETCHED FROM DATABASE ---")
        print(f"ID: {exercise.id}")
        print(f"TITLE: {exercise.title}")
        print(f"SETUP_FILES: {repr(exercise.setup_files)}")
        print("------------------------------------")
        # --- END DEBUG CODE ---

        # --- 2. Create a unique temp directory ---
        unique_id = str(uuid.uuid4())
        host_temp_dir = os.path.join(settings.BASE_DIR, 'temp_code', unique_id)
        os.makedirs(host_temp_dir, exist_ok=True)
        
        # --- 3. Write separate files for setup and user code ---
        user_code_path = os.path.join(host_temp_dir, 'user_code.py')
        with open(user_code_path, 'w') as f:
            f.write(code)
            
        setup_code_path = os.path.join(host_temp_dir, 'setup.py')
        with open(setup_code_path, 'w') as f:
            f.write(exercise.setup_code)
            
        # --- 4. Write setup_files (for file I/O) ---
        if exercise.setup_files:
            for file_name, file_content in exercise.setup_files.items():
                file_path = os.path.join(host_temp_dir, file_name)
                with open(file_path, 'w') as f:
                    f.write(file_content)

        # --- 5. Build the JSON Config ---
        test_cases = []
        for tc in exercise.tests.all():
            test_cases.append({
                "name": tc.name, "type": tc.test_type, "inputs": tc.inputs,
                "stdin": tc.stdin_data, "expected_output": tc.expected_output,
                "is_hidden": tc.is_hidden
            })
        
        config = {
            "exercise_id": str(exercise.id),
            "function_to_test": exercise.function_to_test,
            "module_name": 'user_code',
            "test_cases": test_cases
        }
        config_json_string = json.dumps(config)

        # --- 6. Define the Docker "BYPASS" Command ---
        docker_cmd = [
            'docker', 'run', '--rm', '-i',
            '--net=none', '--memory=128m', '--pids-limit=100',
            
            # Mount 1: The ENTIRE temp directory (with user_code.py, setup.py, etc.)
            '-v', f'{host_temp_dir}:/app',
            
            # Mount 2: Our test runner script (read-only)
            '-v', f'{RUNNER_SCRIPT_PATH}:/app/run_tests.py:ro',
            
            '-w', '/app',
            
            # Use the official image, NOT 'python-sandbox'
            'python:3.11-slim', 
            
            # The command to run
            '/usr/local/bin/python3.11', '/app/run_tests.py'
        ]

        # --- 7. Execute the Command ---
        process = subprocess.run(
            docker_cmd,
            input=config_json_string.encode('utf-8'),
            capture_output=True,
            timeout=10,
        )

        # --- 8. Process the Result ---
        if process.returncode == 0:
            try:
                result_json = json.loads(process.stdout.decode('utf-8'))
                return JsonResponse(result_json)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Test runner gave invalid JSON output.', 'output': process.stdout.decode('utf-8')}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Test runner failed to execute.', 'stderr': (f"RETURN CODE: {process.returncode}\n\n" f"--- STDOUT ---\n{process.stdout.decode('utf-8')}\n\n" f"--- STDERR ---\n{process.stderr.decode('utf-8')}")}, status=400)

    except subprocess.TimeoutExpired:
        return JsonResponse({'status': 'error', 'message': 'Your code took too long to run (timeout).'}, status=408)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)
    
    finally:
        # --- 9. Clean up ---
        if host_temp_dir and os.path.exists(host_temp_dir):
            try:
                shutil.rmtree(host_temp_dir)
            except OSError as e:
                print(f"Error removing temp directory {host_temp_dir}: {e}")