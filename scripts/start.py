import subprocess
from pathlib import Path
import os


def run():
    src_path = Path(__file__).resolve().parent.parent / 'src'

    os.environ['PYTHONPATH'] = str(src_path)

    app = Path(__file__).resolve().parent.parent / 'src' / 'GUI_qt' / '__init__.py'

    result = subprocess.run(["python", str(app)], capture_output=True, text=True, env=os.environ)

    output = result.stdout
    error = result.stderr

    print("Output App:")
    print(output)

    if error:
        print("Errors app:")
        print(error)
