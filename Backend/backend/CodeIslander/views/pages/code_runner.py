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
from ...models import Exercise, Tests 

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

@csrf_exempt
def run_code_secure(request, exercise_id):
    """
    This view runs user code against database-driven test cases
    inside a secure Docker container.
    
    It builds a JSON config from the database, pipes it to the
    container's stdin, and returns the JSON result from stdout.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    host_path = None
    try:
        body = json.loads(request.body)
        code = body.get('code', '')

        if not code:
            return JsonResponse({'error': 'No code provided.'}, status=400)

        temp_dir = os.path.join(settings.BASE_DIR, 'temp_code')
        os.makedirs(temp_dir, exist_ok=True)
        
        unique_id = str(uuid.uuid4())
        host_path = os.path.join(temp_dir, f'user_code_{unique_id}.py')
        
        with open(host_path, 'w') as f:
            f.write(code)

        exercise = get_object_or_404(
            Exercise.objects.prefetch_related('tests'), 
            pk=exercise_id
        )

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
        
        docker_cmd = [
            'docker', 'run',
            '--rm',
            '-i',
            '--net=none',
            '--memory=128m',
            '--pids-limit=100',
            
            '-v', f'{host_path}:/app/user_code.py:ro',
            
            'python-sandbox', 

            '/usr/local/bin/python3.11', '/app/run_tests.py'
        ]
        
        process = subprocess.run(
            docker_cmd,
            input=config_json_string.encode('utf-8'),
            capture_output=True,
            timeout=10,
        )

        if process.returncode == 0:
            try:
                result_json = json.loads(process.stdout.decode('utf-8'))
                return JsonResponse(result_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Test runner gave invalid JSON output.',
                    'output': process.stdout.decode('utf-8')
                }, status=500)
        else:
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
        return JsonResponse({
            'status': 'error', 
            'message': 'Your code took too long to run (timeout).'
            }, status=408)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'An unexpected error occurred: {str(e)}'
            }, status=500)
    
    finally:
        if host_path and os.path.exists(host_path):
            try:
                os.remove(host_path)
            except OSError as e:
                print(f"Error removing temp file {host_path}: {e}")