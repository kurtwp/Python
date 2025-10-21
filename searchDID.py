import os
import subprocess

outPut = "outFile.txt"

# Get phone number to search
phoneNumber = input("Enter phone number to be searched: ")



for x in os.listdir():
        if x == outPut:
                # Prints only text file present in My Folder
                print("Found file and removing:", x)
                os.remove("outFile.txt")
i = 0
with open(outPut, 'w') as f:
        for line in os.listdir():
                if line.endswith(".pcap"):
                        print(f"Searching file: {line}")
                        f.write(f"------------------ File: {line}\n")
                        command = ["tshark", "-r", line, "-Y", f"sip contains {phoneNumber}"]
                        result = subprocess.run(command, capture_output=True, text=True)
                        f.write(result.stdout)
                        i += 1
print(f"{i} File Searched!")
print("Calls can be found in file: " + outPut)
