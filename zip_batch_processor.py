import subprocess
import os
import threading

# Function to set Git user configuration
def set_git_config():
    try:
        # Set user email and name for Git
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)
        print("[Success] Git user configuration set.")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to set Git configuration: {e}")

# Function to extract a single file using 7z and check its actual output location
def extract_file(zip_path, file):
    try:
        # Extracting file with directory structure
        result = subprocess.run(['7z', 'x', zip_path, file, '-o./extracted'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Extract the output from stdout to verify where the file was extracted
        output = result.stdout
        print(output)  # Optionally print the extraction output for debugging
        
        # Check the extracted file's path based on the output
        extracted_file_path = f"./extracted/{file}"
        if os.path.isfile(extracted_file_path):
            print(f"[Success] Extracted: {extracted_file_path}")
            return extracted_file_path
        else:
            print(f"[Error] Extracted, but file not found in expected path: {extracted_file_path}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to extract {file}: {e}")
        return None

# Function to commit and push a batch of files together
def git_commit_and_push(files):
    try:
        # Stage all files in the batch
        for file in files:
            if os.path.isfile(file):
                subprocess.run(["git", "add", file], check=True)
            else:
                print(f"[Error] File not found for git add: {file}")
        
        # Commit all staged files together
        subprocess.run(["git", "commit", "-m", "Batch add of extracted files"], check=True)
        # Push all committed changes
        subprocess.run(["git", "push", "origin", "main"], check=True)

        # Clean up the files after push
        for file in files:
            os.remove(file)
            print(f"[Success] Pushed and deleted: {file}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Git operation failed for batch: {e}")
    except Exception as e:
        print(f"[Error] Failed to delete files: {e}")

# Process each batch by extracting files and pushing them to the repository
def process_batch(zip_path, batch):
    extracted_files = []
    for file in batch:
        extracted_file = extract_file(zip_path, file)
        if extracted_file:
            extracted_files.append(extracted_file)
    
    # Once all files in the batch are extracted, commit and push them together
    if extracted_files:
        git_commit_and_push(extracted_files)

# Main function to process files in batches
def main():
    zip_path = 'zbbig2.zip'  # Path to the ZIP file
    batch_size = 5  # Set the desired batch size

    # Set Git configuration for user identity
    set_git_config()

    # Create a directory for extracted files if not exists
    if not os.path.exists('./extracted'):
        os.makedirs('./extracted')

    # Read the list of files to be processed from file_list.txt
    with open('file_list.txt', 'r') as f:
        files = f.read().splitlines()

    # Split files into batches and process each batch
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        process_batch(zip_path, batch)

if __name__ == "__main__":
    main()
