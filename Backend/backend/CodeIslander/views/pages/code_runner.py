import docker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

# Initialize the Docker client
# This connects to the Docker daemon on your server
try:
    client = docker.from_env()
except docker.errors.DockerException:
    # Handle the case where Docker is not running or accessible
    client = None

def code_runner_page(request):
    """
    This view handles the GET request to display the code runner page.
    """
    return render(request, 'runner.html')

@csrf_exempt
def run_code_secure(request):
    if not client:
        return JsonResponse({'error': 'Docker service is not available.'}, status=503)

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            code = body.get('code', '')

            if not code:
                return JsonResponse({'error': 'No code provided.'}, status=400)

            # Run the code inside our secure Docker container
            # This is the core of our secure runner
            container = client.containers.run(
                'python-sandbox',  # The image we built
                command=['python', '-c', code],
                detach=True,       # Run in the background
                mem_limit='128m',  # Max memory: 128 MB
                network_disabled=True, # CRITICAL: Disable all networking
                pids_limit=100,      # Limit the number of processes
                remove=False       # Don't remove immediately, we need logs
            )

            # Wait for the container to finish, with a strict timeout
            result = container.wait(timeout=5)
            
            # Get logs (stdout and stderr)
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

            # Clean up the container now that we're done
            container.remove()

            # The exit code tells us if the code ran successfully
            if result['StatusCode'] == 0:
                output = stdout
            else:
                output = stderr
            
            return JsonResponse({'output': output})

        except docker.errors.ContainerError as e:
            # This catches errors from within the container (e.g., Python syntax errors)
            container.remove()
            return JsonResponse({'error': str(e)})
        except Exception as e:
            # This catches other errors, like the timeout
            # If a container exists from a timed-out run, try to clean it up
            try:
                container.stop()
                container.remove()
            except NameError:
                pass # container was not created
            return JsonResponse({'error': f'An execution error occurred: {str(e)}'}, status=408)
            
    return JsonResponse({'error': 'Invalid request method.'}, status=405)