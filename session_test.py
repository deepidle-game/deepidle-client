import subprocess
import time
import os
import fcntl
import shlex

command = "opencode"
flags = ""

try:
    process = subprocess.Popen(
        [command] + shlex.split(flags),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=os.environ
    )
    
    fd = process.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    print(f"Process started (PID: {process.pid})")
    
    # Wait and read
    for i in range(50):
        try:
            line = process.stdout.readline()
            if line:
                print(f"OUT: {repr(line)}")
            else:
                pass
        except IOError:
            pass
        time.sleep(0.1)
        
    print("Sending 'ping'...")
    process.stdin.write("ping\n")
    process.stdin.flush()
    
    for i in range(50):
        try:
            line = process.stdout.readline()
            if line:
                print(f"OUT: {repr(line)}")
        except IOError:
            pass
        time.sleep(0.1)

    process.terminate()
except Exception as e:
    print(f"Error: {e}")
