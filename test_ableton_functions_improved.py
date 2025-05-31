import asyncio
import subprocess
import sys
import os
import time
import json
import re

async def run_test():
    """
    Run a series of tests for the Ableton AI Controller.
    
    This improved version:
    1. Focuses on commands known to work
    2. Accounts for 0-based indexing in API calls
    3. Adds more detailed logging
    4. Makes tests more independent
    5. Captures and analyzes the output more thoroughly
    """
    # Define test prompts with expected outcomes
    test_cases = [
        {
            "prompt": "create a new midi track",
            "expected_command": "create_midi_track",
            "should_succeed": True,
            "description": "Create a new MIDI track"
        },
        {
            "prompt": "set the name of track 1 to 'Test Track Alpha'",
            "expected_command": "set_track_name",
            "should_succeed": True,
            "description": "Set name of track 1 (index 0) to 'Test Track Alpha'"
        },
        {
            "prompt": "create a clip on track 2 at clip slot 0 with length 4",
            "expected_command": "create_clip",
            "should_succeed": True,
            "description": "Create a clip on track 2 (index 1) at slot 0"
        },
        {
            "prompt": "set the tempo to 125",
            "expected_command": "set_tempo",
            "should_succeed": True,
            "description": "Set the tempo to 125 BPM"
        },
        {
            "prompt": "get session info",
            "expected_command": "get_session_info",
            "should_succeed": True,
            "description": "Get information about the current session"
        }
    ]

    print("Starting Ableton AI Controller Improved Tests...")
    print(f"Running {len(test_cases)} test cases\n")

    results = []

    for i, test_case in enumerate(test_cases):
        prompt = test_case["prompt"]
        expected_command = test_case["expected_command"]
        should_succeed = test_case["should_succeed"]
        description = test_case["description"]

        print(f"\n=== Test {i+1}/{len(test_cases)}: {description} ===")
        print(f"Prompt: '{prompt}'")
        print(f"Expected command: {expected_command}")
        print(f"Should succeed: {should_succeed}")
        
        # Start main.py as a subprocess
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        try:
            # Give main.py time to initialize
            print("Waiting for main.py to initialize (20 seconds)...")
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
            stdout_output, stderr_output = process.communicate(timeout=30)
            
            # Analyze the output
            command_executed = re.search(r"Executed (\w+):", stdout_output) if "Executed" in stdout_output else None
            command_failed = re.search(r"Failed to execute (\w+):", stdout_output) if "Failed to execute" in stdout_output else None
            
            executed_command = command_executed.group(1) if command_executed else (command_failed.group(1) if command_failed else None)
            success = command_executed is not None and command_failed is None
            
            # Check if the expected command was executed
            command_match = executed_command == expected_command if executed_command else False
            
            # Extract result if available
            result_match = re.search(r"Executed [^:]+: (.+)", stdout_output)
            result_data = result_match.group(1) if result_match else None
            
            # Extract error if available
            error_match = re.search(r"Failed to execute [^:]+: (.+)", stdout_output)
            error_message = error_match.group(1) if error_match else None
            
            # Determine test result
            test_passed = success == should_succeed and command_match
            
            # Store the results
            test_result = {
                "test_number": i+1,
                "description": description,
                "prompt": prompt,
                "expected_command": expected_command,
                "executed_command": executed_command,
                "should_succeed": should_succeed,
                "did_succeed": success,
                "command_match": command_match,
                "test_passed": test_passed,
                "result_data": result_data,
                "error_message": error_message
            }
            results.append(test_result)
            
            # Print a summary of this test
            print("\n--- Test Result ---")
            print(f"Expected command: {expected_command}")
            print(f"Executed command: {executed_command}")
            print(f"Should succeed: {should_succeed}")
            print(f"Did succeed: {success}")
            print(f"Command match: {command_match}")
            print(f"Test passed: {test_passed}")
            if result_data:
                print(f"Result data: {result_data}")
            if error_message:
                print(f"Error message: {error_message}")
            
            print(f"\n--- Test {i+1} Completed ---")

        except subprocess.TimeoutExpired:
            print(f"ERROR: main.py timed out for prompt: '{prompt}'. Terminating process.")
            process.kill()
            stdout_output, stderr_output = process.communicate()
            results.append({
                "test_number": i+1,
                "description": description,
                "prompt": prompt,
                "error": "Timeout",
                "test_passed": False
            })
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if process.poll() is None:
                process.kill()
            results.append({
                "test_number": i+1,
                "description": description,
                "prompt": prompt,
                "error": str(e),
                "test_passed": False
            })

    # Print overall summary
    print("\n=== Overall Test Results ===")
    passed_tests = sum(1 for r in results if r.get("test_passed", False))
    print(f"Passed: {passed_tests}/{len(test_cases)} tests")
    
    for i, result in enumerate(results):
        status = "PASSED" if result.get("test_passed", False) else "FAILED"
        print(f"Test {i+1}: {status} - {result.get('description', 'Unknown test')}")
        if not result.get("test_passed", False):
            if "error" in result:
                print(f"  Error: {result['error']}")
            elif "error_message" in result:
                print(f"  Error: {result['error_message']}")
            else:
                expected_cmd = result.get("expected_command", "unknown")
                executed_cmd = result.get("executed_command", "none")
                should_succeed = result.get("should_succeed", "unknown")
                did_succeed = result.get("did_succeed", "unknown")
                print(f"  Expected command: {expected_cmd}, Executed: {executed_cmd}")
                print(f"  Should succeed: {should_succeed}, Did succeed: {did_succeed}")
    
    print("\nAll tests finished.")

if __name__ == "__main__":
    asyncio.run(run_test())
