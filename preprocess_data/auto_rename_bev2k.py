import os
import subprocess
from tqdm import tqdm

def find_images_folders(root_path):
    # Count total folders for tqdm progress bar
    total_folders = sum([len(dirs) for _, dirs, _ in os.walk(root_path) if _ == 2])
    progress_bar = tqdm(total=total_folders, desc="Processing folders", unit="folder")

    for root, dirs, files in os.walk(root_path):
        # Check if we are at the second level subfolder
        if root.count(os.sep) - root_path.count(os.sep) == 2:
            if 'images' in dirs:
                images_folder_path = os.path.join(root, 'images')
                # Execute rename_jpg.py script with images_folder_path as argument
                subprocess.run(['python', 'rename_jpg.py', images_folder_path])
                progress_bar.update(1)  # Update progress bar

    progress_bar.close()  # Close progress bar when done

if __name__ == "__main__":
    current_path = '.'  # You can replace '.' with your desired starting path
    find_images_folders(current_path)
