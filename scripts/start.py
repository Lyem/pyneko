import os
import subprocess
from pathlib import Path
from sys import platform

is_posix = platform.startswith(("darwin", "cygwin", "linux", "linux2"))

def run():
    src_path = Path(__file__).resolve().parent.parent / 'src'

    app = Path(__file__).resolve().parent.parent / 'src' / 'GUI_qt' / '__init__.py'

    os.environ['PYNEKOENV'] = 'dev'

    if(is_posix):
        os.environ['PYTHONPATH'] = str(src_path)

        result = subprocess.run(["jurigged", str(app)], capture_output=True, text=True, env=os.environ)
    else:
        script = f"set PYTHONPATH={str(src_path)} && jurigged {str(app)}"
        result = subprocess.run(script, capture_output=True, text=True, shell=True)

    output = result.stdout
    error = result.stderr

    print("Output App:")
    print(output)

    if error:
        print("Errors app:")
        print(error)

if __name__ == "__main__":
    run()
