import subprocess
import glob
import sys

def main():
    """
    Searches for a phone number in SIP protocol traffic within .pcap files.
    """
    # 1. Get user input for the phone number
    try:
        phone_number = input("Enter phone number to be searched: ")
    except EOFError:
        # Handle cases where input is not from a terminal (e.g., in a script)
        print("Error: Could not read input. Make sure to run this script interactively.")
        sys.exit(1)

    # 2. Define file patterns and output file
    capture_files_pattern = "*.pcap"
    output_file_name = "outPutFile.txt"

    # 3. Use glob to find all matching files
    capture_files = glob.glob(capture_files_pattern)
    if not capture_files:
        print(f"No files matching '{capture_files_pattern}' found.")
        return

    # 4. Open the output file in write mode ('w') to clear its contents
    # Use 'a' if you want to append, but the bash script's logic implies a fresh run
    # with redirection (>>), so we'll start fresh.
    with open(output_file_name, "w") as output_file:
        # 5. Loop through each file found
        for file in capture_files:
            print(f"Searching file: {file}")
            
            # 6. Write a header for the current file to the output file
            output_file.write(f" -------- File: {file}\n")
            
            # 7. Construct the tshark command
            # The -Y filter is used to apply a display filter
            command = [
                "tshark",
                "-r", file,
                "-Y", f"sip contains {phone_number}"
            ]
            
            try:
                # 8. Run the tshark command and capture its output
                # `capture_output=True` captures stdout and stderr
                # `text=True` decodes the output as text
                # `check=True` raises an exception if the command fails
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 9. Write the command's output to the output file
                output_file.write(result.stdout)
            
            except subprocess.CalledProcessError as e:
                # 10. Handle errors, such as tshark not being found or command issues
                print(f"Error executing tshark for file {file}: {e.stderr}", file=sys.stderr)
            except FileNotFoundError:
                print("Error: tshark not found. Please ensure it is installed and in your system's PATH.", file=sys.stderr)
                sys.exit(1)

    # 11. Inform the user that the search has finished
    print(f"Search has completed. See file '{output_file_name}'!")

if __name__ == "__main__":
    main()
