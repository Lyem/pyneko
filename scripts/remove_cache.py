import shutil
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def remove_cache_folders():
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file == '__init__.spec':
                os.remove(file)
        for folder in dirs:
            if folder == "__pycache__" or folder == ".pytest_cache" or folder == "build" or folder == "dist":
                folder_path = os.path.join(root, folder)
                shutil.rmtree(folder_path)


if __name__ == "__main__":
    remove_cache_folders()