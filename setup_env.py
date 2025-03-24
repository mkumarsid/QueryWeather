import subprocess
import sys
import os
import shutil

def is_poetry_installed():
    return shutil.which("poetry") is not None

def install_poetry():
    print("📦 Installing Poetry...")
    install_cmd = (
        "curl -sSL https://install.python-poetry.org | python3 -"
        if shutil.which("curl")
        else "pip install poetry"
    )
    subprocess.run(install_cmd, shell=True, check=True)
    print("✅ Poetry installed successfully!")

def run_command(command):
    print(f"▶️ Running: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    if not is_poetry_installed():
        install_poetry()

    print("\n📁 Setting up virtual environment and installing dependencies...")
    run_command("poetry config virtualenvs.in-project true")
    run_command("poetry install --no-root")

    print("\n✅ Setup complete! To activate your virtual environment, run:")
    print("   source .venv/bin/activate   # On Linux/macOS")
    print("   .venv\\Scripts\\activate     # On Windows")

    print("\n🚀 Now you can run your local script:")
    print("   poetry run python scripts/run_local.py")

if __name__ == "__main__":
    main()
