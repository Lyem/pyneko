import re

def sanitize_folder_name(folder_name):
        name = (folder_name[:20]) if len(folder_name) > 20 else folder_name
        sanitized_name = re.sub(r'[\\/:*?"<>|]', '', name)
        return sanitized_name.strip()