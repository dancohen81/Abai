import asyncio
import subprocess
import sys
import os
import time
import json
import re

async def run_test():
    """
    Run a comprehensive series of tests for the Ableton AI Controller.
    
    This version:
    1. Tests both supported and unsupported commands
    2. Accounts for 0-based indexing in API calls
    3. Provides detailed logging and analysis
    4. Makes tests independent where possible
    5. Includes expected failures to verify error handling
    """
    # Define test prompts with expected outcomes
    test_cases = [
        # Tests for supported commands (expected to succeed)
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
            "prompt": "create a clip on track 2 at clip slot 1 with length 4",
            "expected_command": "create_clip",
            "should_succeed": True,
            "description": "Create a clip on track 2 (index 1) at slot 1"
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
        },
        
        # Tests for unsupported commands (expected to fail)
        {
            "prompt": "create a new audio track",
            "expected_command": "create_audio_track",
            "should_succeed": False,
            "description": "Create a new audio track (unsupported command)"
        },
        {
            "prompt": "delete track 3",
            "expected_command": "delete_track",
            "should_succeed": False,
            "description": "Delete track 3 (unsupported command)"
        },
        {
            "prompt": "save project to 'test_project.als'",
            "expected_command": "save_project",
            "should_succeed": False,
            "description": "Save project (unsupported command)"
        },
        
        # Tests for commands with known issues
        {
            "prompt": "start playback",
            "expected_command": "start_playback",
            "should_succeed": False,
            "description": "Start playback (known issue with NoneType)"
        },
        {
            "prompt": "stop playback",
            "expected_command": "stop_playback",
            "should_succeed": False,
            "description": "Stop playback (known issue with NoneType)"
        },
        
        # Additional tests for supported commands
        {
            "prompt": "create a clip on track 3 at clip slot 2 with length 2",
            "expected_command": "create_clip",
            "should_succeed": True,
            "description": "Create another clip on a different track and slot"
        },
        {
            "prompt": "set the name of track 2 to 'Melody Track'",
            "expected_command": "set_track_name",
            "should_succeed": True,
            "description": "Set name of another track"
        }
    ]

    print("Starting Ableton AI Controller Comprehensive Tests...")
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
            
            # For save_project, check for the special message
            if "Failed to save project:" in stdout_output:
                error_match = re.search(r"Failed to save project: (.+)", stdout_output)
                error_message = error_match.group(1) if error_match else None
                executed_command = "save_project"
                success = False
                command_match = executed_command == expected_command
            
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
    
    # Group results by category
    successful_tests = [r for r in results if r.get("test_passed", False) and r.get("should_succeed", False)]
    expected_failures = [r for r in results if r.get("test_passed", False) and not r.get("should_succeed", True)]
    unexpected_failures = [r for r in results if not r.get("test_passed", False) and r.get("should_succeed", True)]
    unexpected_successes = [r for r in results if not r.get("test_passed", False) and not r.get("should_succeed", True)]
    
    print(f"\nSuccessful tests: {len(successful_tests)}")
    for result in successful_tests:
        print(f"  Test {result['test_number']}: {result['description']}")
    
    print(f"\nExpected failures: {len(expected_failures)}")
    for result in expected_failures:
        print(f"  Test {result['test_number']}: {result['description']}")
        if "error_message" in result and result["error_message"]:
            print(f"    Error: {result['error_message']}")
    
    if unexpected_failures:
        print(f"\nUnexpected failures: {len(unexpected_failures)}")
        for result in unexpected_failures:
            print(f"  Test {result['test_number']}: {result['description']}")
            if "error" in result:
                print(f"    Error: {result['error']}")
            elif "error_message" in result:
                print(f"    Error: {result['error_message']}")
    
    if unexpected_successes:
        print(f"\nUnexpected successes: {len(unexpected_successes)}")
        for result in unexpected_successes:
            print(f"  Test {result['test_number']}: {result['description']}")
    
    print("\nAll tests finished.")

if __name__ == "__main__":
    asyncio.run(run_test())
