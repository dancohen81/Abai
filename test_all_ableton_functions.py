import asyncio
import subprocess
import sys
import os
import time
import json
import re

async def run_test():
    """
    Run a comprehensive test of all possible Ableton API functions.
    
    This script:
    1. Tests all functions listed in the Ableton API wrapper
    2. Accounts for 0-based track indexing and 1-based clip slot indexing
    3. Provides detailed logging and analysis
    4. Categorizes functions as working, not working, or having issues
    """
    # Define test prompts for all possible Ableton functions
    test_cases = [
        # Basic track operations
        {
            "prompt": "create a new midi track",
            "expected_command": "create_midi_track",
            "description": "Create a new MIDI track"
        },
        {
            "prompt": "create a new audio track",
            "expected_command": "create_audio_track",
            "description": "Create a new audio track"
        },
        {
            "prompt": "set the name of track 1 to 'Test Track'",
            "expected_command": "set_track_name",
            "description": "Set name of track 1 (index 0)"
        },
        {
            "prompt": "delete track 3",
            "expected_command": "delete_track",
            "description": "Delete track 3"
        },
        
        # Clip operations
        {
            "prompt": "create a clip on track 1 at clip slot 1 with length 4",
            "expected_command": "create_clip",
            "description": "Create a clip on track 1 at slot 1"
        },
        {
            "prompt": "add notes to the clip on track 1 at clip slot 1 with pitches 60, 64, 67 and durations 0.5",
            "expected_command": "add_notes_to_clip",
            "description": "Add notes to a clip"
        },
        {
            "prompt": "set the name of the clip on track 1 at clip slot 1 to 'Test Clip'",
            "expected_command": "set_clip_name",
            "description": "Set clip name"
        },
        {
            "prompt": "fire the clip on track 1 at clip slot 1",
            "expected_command": "fire_clip",
            "description": "Fire a clip"
        },
        {
            "prompt": "stop the clip on track 1",
            "expected_command": "stop_clip",
            "description": "Stop a clip"
        },
        {
            "prompt": "duplicate the clip on track 1 at clip slot 1 to clip slot 2",
            "expected_command": "duplicate_clip",
            "description": "Duplicate a clip"
        },
        {
            "prompt": "delete the clip on track 1 at clip slot 2",
            "expected_command": "delete_clip",
            "description": "Delete a clip"
        },
        {
            "prompt": "move the clip on track 1 at clip slot 1 to track 2 at clip slot 1",
            "expected_command": "move_clip",
            "description": "Move a clip"
        },
        {
            "prompt": "set the loop start and end of the clip on track 1 at clip slot 1 to 1.0 and 3.0",
            "expected_command": "set_clip_loop_attributes",
            "description": "Set clip loop attributes"
        },
        {
            "prompt": "set the start and end time of the clip on track 1 at clip slot 1 to 0.5 and 3.5",
            "expected_command": "set_clip_start_end",
            "description": "Set clip start and end times"
        },
        {
            "prompt": "set the quantization of the clip on track 1 at clip slot 1 to 1/16",
            "expected_command": "set_clip_quantization",
            "description": "Set clip quantization"
        },
        {
            "prompt": "update notes in the clip on track 1 at clip slot 1 to have pitches 62, 65, 69",
            "expected_command": "update_notes_in_clip",
            "description": "Update notes in a clip"
        },
        {
            "prompt": "delete all notes from the clip on track 1 at clip slot 1",
            "expected_command": "delete_notes_from_clip",
            "description": "Delete notes from a clip"
        },
        
        # Session operations
        {
            "prompt": "set the tempo to 130",
            "expected_command": "set_tempo",
            "description": "Set the tempo"
        },
        {
            "prompt": "start playback",
            "expected_command": "start_playback",
            "description": "Start playback"
        },
        {
            "prompt": "stop playback",
            "expected_command": "stop_playback",
            "description": "Stop playback"
        },
        {
            "prompt": "save project to 'test_project.als'",
            "expected_command": "save_project",
            "description": "Save project"
        },
        
        # Device and mixer operations
        {
            "prompt": "load a reverb effect on track 1",
            "expected_command": "load_instrument_or_effect",
            "description": "Load an instrument or effect"
        },
        {
            "prompt": "set the dry/wet parameter of the reverb on track 1 to 50%",
            "expected_command": "set_device_parameter",
            "description": "Set device parameter"
        },
        {
            "prompt": "create a return track",
            "expected_command": "create_return_track",
            "description": "Create a return track"
        },
        {
            "prompt": "set the send level from track 1 to return track A to 0.5",
            "expected_command": "set_send_level",
            "description": "Set send level"
        },
        {
            "prompt": "set the volume of track 1 to -6 dB",
            "expected_command": "set_track_volume",
            "description": "Set track volume"
        },
        {
            "prompt": "set the pan of track 1 to 0.3 (slightly right)",
            "expected_command": "set_track_pan",
            "description": "Set track pan"
        },
        
        # Information retrieval
        {
            "prompt": "get session info",
            "expected_command": "get_session_info",
            "description": "Get session information"
        }
    ]

    print("Starting Ableton AI Controller All Functions Test...")
    print(f"Testing {len(test_cases)} Ableton functions\n")

    results = []

    for i, test_case in enumerate(test_cases):
        prompt = test_case["prompt"]
        expected_command = test_case["expected_command"]
        description = test_case["description"]

        print(f"\n=== Test {i+1}/{len(test_cases)}: {description} ===")
        print(f"Prompt: '{prompt}'")
        print(f"Expected command: {expected_command}")
        
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
            
            # Store the results
            test_result = {
                "test_number": i+1,
                "description": description,
                "prompt": prompt,
                "expected_command": expected_command,
                "executed_command": executed_command,
                "did_succeed": success,
                "command_match": command_match,
                "result_data": result_data,
                "error_message": error_message
            }
            results.append(test_result)
            
            # Print a summary of this test
            print("\n--- Test Result ---")
            print(f"Expected command: {expected_command}")
            print(f"Executed command: {executed_command}")
            print(f"Did succeed: {success}")
            print(f"Command match: {command_match}")
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
                "did_succeed": False,
                "command_match": False
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
                "did_succeed": False,
                "command_match": False
            })

    # Categorize results
    working_functions = []
    not_working_functions = []
    issue_functions = []

    for result in results:
        if result.get("did_succeed", False) and result.get("command_match", False):
            working_functions.append(result)
        elif not result.get("command_match", False) or "Unknown command" in result.get("error_message", ""):
            not_working_functions.append(result)
        else:
            issue_functions.append(result)

    # Print overall summary
    print("\n=== Ableton API Functions Test Results ===")
    print(f"Total functions tested: {len(test_cases)}")
    print(f"Working functions: {len(working_functions)}")
    print(f"Non-implemented functions: {len(not_working_functions)}")
    print(f"Functions with issues: {len(issue_functions)}")
    
    print("\n--- Working Functions ---")
    for result in working_functions:
        print(f"  {result['expected_command']}: {result['description']}")
        if "result_data" in result and result["result_data"]:
            print(f"    Example result: {result['result_data']}")
    
    print("\n--- Non-implemented Functions ---")
    for result in not_working_functions:
        print(f"  {result['expected_command']}: {result['description']}")
        if "error_message" in result and result["error_message"]:
            print(f"    Error: {result['error_message']}")
    
    print("\n--- Functions with Issues ---")
    for result in issue_functions:
        print(f"  {result['expected_command']}: {result['description']}")
        if "error_message" in result and result["error_message"]:
            print(f"    Error: {result['error_message']}")
    
    print("\nAll tests finished.")
    
    # Print Ableton API findings
    print("\n=== Ableton API Usage Notes ===")
    print("1. Track Indexing: Tracks are 0-indexed in API calls, but 1-indexed in prompts")
    print("   Example: 'track 1' in prompt corresponds to track_index: 0 in API call")
    print("2. Clip Slot Indexing: Clip slots are 1-indexed in both prompts and API calls")
    print("   Example: 'clip slot 1' in prompt corresponds to clip_index: 0 in API call")
    print("3. Clip Creation Constraints:")
    print("   - Clips can only be created on MIDI tracks")
    print("   - Cannot create a clip in a slot that already has a clip")
    print("4. Function Support:")
    print("   - Working functions can be used reliably")
    print("   - Non-implemented functions are not available in the current API")
    print("   - Functions with issues may work in some cases but have limitations or bugs")

if __name__ == "__main__":
    asyncio.run(run_test())
