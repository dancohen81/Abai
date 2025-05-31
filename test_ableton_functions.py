import asyncio
import subprocess
import sys
import os
import time

async def run_test():
    test_prompts = [
        "create a new midi track",
        "set the name of track 1 to 'My Test Track'",
        "create a clip on track 1 at clip slot 0 with length 8",
        "set the tempo to 120",
        "start playback",
        "stop playback",
        "get session info",
        "create a new audio track",
        "delete track 1",
        "save project to 'test_project.als'"
    ]

    print("Starting Ableton AI Controller tests...")

    for i, prompt in enumerate(test_prompts):
        print(f"\n--- Running Test {i+1}/{len(test_prompts)}: '{prompt}' ---")
        
        # Start main.py as a subprocess
        # We need to ensure main.py can be run in a way that we can feed it input
        # and capture its output. Using Popen with PIPE for stdin/stdout is suitable.
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # Use text mode for string input/output
            bufsize=1 # Line-buffered
        )

        try:
            # Give main.py a moment to initialize and print its initial messages
            time.sleep(20) 
            
            # Send the prompt
            process.stdin.write(prompt + '\n')
            process.stdin.flush()
            print(f"Sent prompt: '{prompt}'")

            # Send 'exit' to terminate main.py after the prompt
            process.stdin.write('exit\n')
            process.stdin.flush()
            print("Sent 'exit' command.")

            # Read output until the process exits
            stdout_output, stderr_output = process.communicate(timeout=30) # Increased timeout
            
            print("\n--- main.py STDOUT ---")
            print(stdout_output)
            print("\n--- main.py STDERR ---")
            print(stderr_output)

            if process.returncode != 0:
                print(f"WARNING: main.py exited with non-zero code {process.returncode} for prompt: '{prompt}'")
            
            print(f"--- Test {i+1} Completed ---")

        except subprocess.TimeoutExpired:
            print(f"ERROR: main.py timed out for prompt: '{prompt}'. Terminating process.")
            process.kill()
            stdout_output, stderr_output = process.communicate()
            print("\n--- main.py STDOUT (after timeout) ---")
            print(stdout_output)
            print("\n--- main.py STDERR (after timeout) ---")
            print(stderr_output)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if process.poll() is None: # If process is still running
                process.kill()

    print("\nAll tests finished.")

if __name__ == "__main__":
    asyncio.run(run_test())
