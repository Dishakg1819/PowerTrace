import docker
import os
import time

def run_code_in_container(code_string):
    client = docker.from_env()
    
    # 1. Write user code to a local temporary file
    temp_filename = "temp_user_script.py"
    with open(temp_filename, "w") as f:
        f.write(code_string)
        
    try:
        # 2. Build a quick ephemeral docker image
        # (We use the current directory context where Dockerfile lives)
        image, build_logs = client.images.build(
            path=".", 
            tags="ecocode-sandbox:latest", 
            rm=True
        )
        
        # 3. Mount and run the script inside the container with strict limits
        start_time = time.time()
        container = client.containers.run(
            "ecocode-sandbox:latest",
            volumes={os.path.abspath(temp_filename): {"bind": "/app/script.py", "mode": "ro"}},
            detach=True,
            mem_limit="256m" # Restrict memory to stabilize measurements
        )
        
        # Wait for container execution to finish and grab logs
        result = container.wait()
        logs = container.logs().decode("utf-8")
        execution_time = time.time() - start_time
        
        container.remove()
        
        # Clean up local temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return {
            "success": True,
            "time": execution_time,
            "logs": logs,
            "error": None
        }
        
    except Exception as e:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return {
            "success": False,
            "time": 0.0,
            "logs": "",
            "error": str(e)
        }