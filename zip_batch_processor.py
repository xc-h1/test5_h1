import subprocess
import os
import threading
from queue import Queue

# Function to set Git user configuration
def set_git_config():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "you@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Your Name"], check=True)
        print("[Success] Git user configuration set.")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to set Git configuration: {e}")

# Function to extract a single file using 7z
def extract_file(zip_path, file, file_queue):
    try:
        result = subprocess.run(['7z', 'x', zip_path, file, '-o./extracted'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        print(output)  # Optionally print the extraction output for debugging

        extracted_file_path = f"./extracted/{file}"
        if os.path.isfile(extracted_file_path):
            print(f"[Success] Extracted: {extracted_file_path}")
            file_queue.put(extracted_file_path)  # Add the extracted file to the queue
        else:
            print(f"[Error] Extracted, but file not found in expected path: {extracted_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to extract {file}: {e}")

# Function to commit and push a batch of files
def git_commit_and_push_batch(file_queue, batch_size):
    batch = []
    try:
        while True:
            # Collect files into a batch
            while not file_queue.empty() and len(batch) < batch_size:
                file = file_queue.get()
                if os.path.isfile(file):
                    subprocess.run(["git", "add", file], check=True)
                    batch.append(file)
            
            if batch:
                # Commit and push the batch
                subprocess.run(["git", "commit", "-m", f"Batch add of {len(batch)} files"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)

                # Remove the files after pushing
                for file in batch:
                    os.remove(file)
                    print(f"[Success] Pushed and deleted: {file}")

                # Clear the batch after processing
                batch.clear()
            else:
                break
    except subprocess.CalledProcessError as e:
        print(f"[Error] Git operation failed: {e}")
    except Exception as e:
        print(f"[Error] Failed to delete files: {e}")

# Main function to extract and push files in batches
def main():
    zip_path = 'zbbig2.zip'  # Path to the ZIP file
    batch_size = 10  # Set the desired batch size
    file_queue = Queue()  # Queue to store extracted files

    # Set Git configuration for user identity
    set_git_config()

    # Create a directory for extracted files if it doesn't exist
    if not os.path.exists('./extracted'):
        os.makedirs('./extracted')

    # Read the list of files to be processed from file_list.txt
    with open('file_list.txt', 'r') as f:
        files = f.read().splitlines()

    # Start the Git push process in a separate thread
    push_thread = threading.Thread(target=git_commit_and_push_batch, args=(file_queue, batch_size))
    push_thread.start()

    # Extract each file in a separate thread
    for file in files:
        threading.Thread(target=extract_file, args=(zip_path, file, file_queue)).start()

    # Wait for the push thread to finish
    push_thread.join()

if __name__ == "__main__":
    main()
