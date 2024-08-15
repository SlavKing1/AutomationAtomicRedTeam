import os
import requests
import zipfile
import subprocess

# Download the ART zip file
url = "https://github.com/redcanaryco/atomic-red-team/archive/refs/heads/master.zip"
response = requests.get(url)

# Creating a folder to extract the zip
folderPath = "C:\\AtomicRedTeam"
os.makedirs(folderPath, exist_ok=True)

# Extract the contents from the zip file to the specified folder folder
zip_file_path = os.path.join(folderPath, "atomic-red-team.zip")
with open(zip_file_path, "wb") as f:
    f.write(response.content)

with zipfile.ZipFile(zip_file_path, "r") as zip_ref: 
    zip_ref.extractall(folderPath)

# Rename the extraction folder
extracted_folder_path = os.path.join(folderPath, "atomic-red-team-master")
target_folder_path = os.path.join(folderPath, "atomic-red-team")
if os.path.exists(extracted_folder_path) and not os.path.exists(target_folder_path):
    os.rename(extracted_folder_path, target_folder_path)

# Delete the zip file
os.remove(zip_file_path)

# Path to Invoke-AtomicRedTeam PowerShell script to run the command and start the test later
invoke_atomic_path = 'C:\\AtomicRedTeam\\atomic-red-team\\invoke-atomicredteam\\invoke-atomicredteam.ps1'
# List of atomics
attacks = ['T1003.001', 'T1006','T1007', 'T1195', 'T1218.002', 'T1003.002']

#os.system("powershell -command powershell -exec bypass")

#def spasenie():
#    subprocess.call('powershell.exe -exec bypass', shell=True)


def run(cmd, filename):
    output_dir = os.path.join(os.getcwd(), "Test_Results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    completed = subprocess.run(cmd, shell=False, check=True, capture_output=True)
    filename = f"{filename}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Check if the scan was successful based on the return code (if the return code is 0 it will proceed if not it will not create the file)
    if completed.returncode == 0:
        with open(filepath, "w") as f:
            f.write(str(completed.stdout.decode()))
    
    return completed

# command = 'powershell.exe -Command "powershell -exec bypass'
# Note: Before entering here it does not accept the bypass code
# Add powershell -command powershell -exec bypass; after the run(" will only execute the bypass but will not go to the next codes Problem

# Loop through each test and run it using Invoke-AtomicRedTeam
attack_results = {}
for attack in attacks:
    # Executing the atomics
    test_result = run("powershell -command \"Import-Module 'C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1'; powershell -command Invoke-AtomicTest "+attack+" -TestNumber 1", str(attack))
    # Checking for prerequisites
    prereq_result = run("powershell -command \"Import-Module 'C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1'; powershell -command Invoke-AtomicTest "+attack+" -CheckPrereqs", str(attack))
    attack_results[attack] = (test_result, prereq_result) #result

# Test Idea to devide both txt files in to two files - One is regarding the data that the test displays after execution and another
# which is the tests after they go through the prerequisites Check
# The txt files that are generated there are - 1: After execution ; 2: After prerequisites are chekced; 3: Asfter prerequisites are applied

    test_output_dir = os.path.join(os.getcwd(), "Test_Results")
    os.makedirs(test_output_dir, exist_ok=True)
    test_output_path = os.path.join(test_output_dir, f"{attack}_Test_Output.txt")
    with open(test_output_path, "w") as f:
        f.write(str(test_result.stdout.decode()))

    # Write the prerequisites output to a corresponding .txt file
    prereq_output_dir = os.path.join(os.getcwd(), "Prereq_Results")
    os.makedirs(prereq_output_dir, exist_ok=True)
    prereq_output_path = os.path.join(prereq_output_dir, f"{attack}_Prereq_Output.txt")
    with open(prereq_output_path, "w") as f:
        f.write(str(prereq_result.stdout.decode()))
#output_str = result.stdout.decode()

# Dictionary for unsuccessfull scans
succ_dict = {"success": 0, "granted": 0, "approved": 0}
unsucc_dict = {"error": 0, "err": 0, "permission": 0, "denied": 0, "fail": 0, "blocked": 0, "problem": 0, "access": 0}
prereq_dict = {"No Preqs": 0, "Elevation required but not provided": 0}

# Iterate through each attack and write the output to the HTML file
with open('Atomics.html', 'w') as f:
    for attack, (test_result, prereq_result) in attack_results.items():
        output_str = test_result.stdout.decode()
        found_unsucc = False
        for word in unsucc_dict:
            if word.lower() in output_str.lower():
                unsucc_dict[word] += 1
                found_unsucc = True
        if found_unsucc:
            f.write(f'<p>{attack} - Fail</p>\n')
        else:
            found_succ = False
            for word in succ_dict:
                if word.lower() in output_str.lower():
                    succ_dict[word] += 1
                    found_succ = True
            if found_succ:
                f.write(f'<p>{attack} - Success</p>\n')
            else:
                f.write(f'<p>{attack} - Success</p>\n')
        
        # Check if any prereqs are required
        prerequisites_present = True
        output_str = prereq_result.stdout.decode()
        for word in prereq_dict:
            if word.lower() in output_str.lower():
                prereq_dict[word] += 1
                prerequisites_present = False
                break
                
        # Output appropriate message based on prereqs
        if prerequisites_present:
            f.write(f'<p>{attack} - Prerequisites required</p>\n')
            # Downloading the prereqs
            result = run("powershell -command \"Import-Module 'C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1'; powershell -command Invoke-AtomicTest "+attack+" -GetPrereqs", str(attack))
        else:
            f.write(f'<p>{attack} - Success with prerequisites</p>\n')
            
    f.write('</body></html>')


# Print the counts of unsuccessful and successful scans
print("Unsuccessful attack counts:", unsucc_dict)
print("Successful attack counts:", succ_dict)
print("Prerequisite required attack counts:", prereq_dict)