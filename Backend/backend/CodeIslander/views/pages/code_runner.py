# Backend/backend/CodeIslander/views.py

import json
import os
import uuid
import docker
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# --- View to Render the HTML Page ---
def code_runner_page(request):
    """
    This view handles the GET request to display the code runner page.
    """
    return render(request, 'runner.html')

# --- View to Securely Execute Code ---

# Initialize the Docker client
try:
    client = docker.from_env()
except docker.errors.DockerException:
    client = None

@csrf_exempt
def run_code_secure(request):
    """
    This view saves user code to a temp file, runs pytest inside a Docker
    container, and returns the detailed test result.
    """
    if not client:
        return JsonResponse({'error': 'Docker service is not available.'}, status=503)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    host_path = None
    container = None
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

        container = client.containers.run(
            'python-sandbox',
            command=['pytest', 'test_user_code.py'],
            detach=True,
            mem_limit='128m',
            network_disabled=True,
            pids_limit=100,
            volumes={
                host_path: {
                    'bind': '/home/sandboxuser/user_code.py',
                    'mode': 'ro'
                }
            },
            remove=False
        )

        result = container.wait(timeout=10)
        
        if result['StatusCode'] == 0:
            output = "✅ OK: All tests passed!"
        else:
            # ** THIS IS THE IMPORTANT UPDATE **
            # If tests fail, get the detailed logs from the container.
            logs = container.logs().decode('utf-8')
            output = (
                "❌ Not OK: One or more tests failed.\n\n"
                "--- Pytest Output ---\n"
                f"{logs}"
            )
        
        return JsonResponse({'output': output})

    except Exception as e:
        return JsonResponse({'error': f'An execution error occurred: {str(e)}'}, status=408)
    
    finally:
        # CRITICAL: Clean up the container and the temporary file.
        try:
            if container:
                container.stop()
                container.remove()
        except docker.errors.NotFound:
            pass
        
        if host_path and os.path.exists(host_path):
            os.remove(host_path)