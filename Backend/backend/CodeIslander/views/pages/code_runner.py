import json
import os
import uuid
import subprocess
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ...models import Exercise, Tests # Make sure this path is correct for your app

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
        # Assuming 'unlockedExercises' is your related field
        perm = request.user.unlockedExercises.filter(pk=exercise.id).exists()
        
    if not perm:
        return redirect("home") # Or any other appropriate redirect
        
    prompt = {'exercise': exercise}
    return render(request, "runner.html", prompt)


    
# --- View to Securely Execute Code ---

@csrf_exempt
def run_code_secure(request, exercise_id):
    """
    This view runs user code against database-driven test cases
    inside a secure Docker container.
    
    It combines hidden setup_code with the user's code,
    pipes a JSON config to the container's stdin,
    and returns the JSON result from stdout.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    host_path = None
    try:
        # --- 1. Get code and Fetch Exercise ---
        body = json.loads(request.body)
        code = body.get('code', '') # This is the user's solution

        if not code:
            return JsonResponse({'error': 'No code provided.'}, status=400)
        
        # Fetch the exercise, its setup_code, and its tests
        exercise = get_object_or_404(
            Exercise.objects.prefetch_related('tests'), 
            pk=exercise_id
        )

        # --- 2. Combine Setup + User Code ---
        # This is the new logic to define variables invisibly
        full_code_to_run = exercise.setup_code + "\n\n" + code

        # --- 3. Save Combined Code to Temp File ---
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_code')
        os.makedirs(temp_dir, exist_ok=True)
        
        unique_id = str(uuid.uuid4())
        host_path = os.path.join(temp_dir, f'user_code_{unique_id}.py')
        
        with open(host_path, 'w') as f:
            f.write(full_code_to_run) # Write the combined code

        # --- 4. Build the JSON Config for the Runner ---
        test_cases = []
        for tc in exercise.tests.all():
            test_cases.append({
                "name": tc.name,
                "type": tc.test_type,
                "inputs": tc.inputs,
                "stdin": tc.stdin_data,
                "expected_output": tc.expected_output,
                "is_hidden": tc.is_hidden
            })
        
        config = {
            "exercise_id": str(exercise.id),
            "function_to_test": exercise.function_to_test,
            "module_name": exercise.module_name,
            "test_cases": test_cases
        }
        config_json_string = json.dumps(config)

        # --- 5. Define the Docker Command ---
        # This uses your clean 'python-sandbox' image
        docker_cmd = [
            'docker', 'run',
            '--rm',             # Automatically remove container on exit
            '-i',               # Keep STDIN open to pipe our config
            '--net=none',       # Disable networking
            '--memory=128m',    # Set memory limit
            '--pids-limit=100', # Set process limit
            '-v', f'{host_path}:/app/user_code.py:ro', # Mount code read-only
            'python-sandbox',   # Your pre-built image
            '/usr/local/bin/python3.11', '/app/run_tests.py' # Run the script
        ]

        # --- 6. Execute the Command ---
        process = subprocess.run(
            docker_cmd,
            input=config_json_string.encode('utf-8'), # Pipe JSON config to stdin
            capture_output=True, # Capture stdout and stderr
            timeout=10,          # Set 10-second timeout
        )

        # --- 7. Process the Result ---
        if process.returncode == 0:
            # Success! The container's stdout is our JSON result
            try:
                result_json = json.loads(process.stdout.decode('utf-8'))
                return JsonResponse(result_json)
            except json.JSONDecodeError:
                # This means run_tests.py printed malformed JSON
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Test runner gave invalid JSON output.',
                    'output': process.stdout.decode('utf-8')
                }, status=500)
        else:
            # The docker command failed OR the runner script crashed
            return JsonResponse({
                'status': 'error', 
                'message': 'Test runner failed to execute.',
                'stderr': (
                    f"RETURN CODE: {process.returncode}\n\n"
                    f"--- STDOUT ---\n{process.stdout.decode('utf-8')}\n\n"
                    f"--- STDERR ---\n{process.stderr.decode('utf-8')}"
                )
            }, status=400)

    except subprocess.TimeoutExpired:
        # The 'timeout=10' in subprocess.run() was hit
        return JsonResponse({
            'status': 'error', 
            'message': 'Your code took too long to run (timeout).'
            }, status=408)
    
    except Exception as e:
        # Catch any other unexpected errors
        return JsonResponse({
            'status': 'error', 
            'message': f'An unexpected error occurred: {str(e)}'
            }, status=500)
    
    finally:
        # --- 8. CRITICAL: Clean up the temp file ---
        if host_path and os.path.exists(host_path):
            try:
                os.remove(host_path)
            except OSError as e:
                # Log this error, as it's bad to leave temp files
                print(f"Error removing temp file {host_path}: {e}")