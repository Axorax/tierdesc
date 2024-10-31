import sys
import subprocess

def build():
    command = [
        sys.executable, '-m', 'PyInstaller',
        '--name=tierdesc',
        '--onefile',
        '--strip',
        '--paths=env\\Lib\\site-packages',
        '--icon=tierdesc.ico',
        '--exclude-module=numpy',
        'main.py'
    ]

    try:
        subprocess.check_call(command)
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
