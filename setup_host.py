#!/usr/bin/env python3
"""
RakijaGSI Host Setup Script
Clean Termux environment setup using root-repo for erofs-utils.
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(ROOT, ".venv")
VENV_PYTHON = os.path.join(VENV, "bin", "python")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")

TERMUX_PACKAGES = [
    "python",
    "python-pip",
    "python-psutil",
    "aria2",
    "openjdk-21",
    "curl",
    "ca-certificates",
    "cmake",
    "ninja",
    "pkg-config",
    "clang",
    "make",
    "git",
    "protobuf",
    "brotli",
    "lz4",
    "zstd",
    "openssl",
    "android-tools",
    "erofs-utils",
]


def log(msg):
    print(f"\033[1m==> {msg}\033[0m", flush=True)


def die(msg):
    print(f"\033[31merror:\033[0m {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, env=None):
    try:
        subprocess.run(cmd, check=True, env=env)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        die(f"Command failed: {cmd} ({e})")


def setup_termux_repos_and_packages():
    log("Enabling root-repo for system tools (erofs-utils)...")
    run(["pkg", "install", "root-repo", "-y"])
    
    log("Updating Termux package lists...")
    run(["pkg", "update", "-y"])

    log("Installing required system packages...")
    run(["pkg", "install", "-y"] + TERMUX_PACKAGES)


def setup_python_environment():
    if os.path.exists(VENV):
        log("Cleaning existing virtual environment...")
        shutil.rmtree(VENV)

    log("Creating Python virtual environment...")
    run(["python", "-m", "venv", "--system-site-packages", "--without-pip", VENV])

    log("Installing pyppmd (with Android Bionic compatibility flags)...")
    env = os.environ.copy()
    env["CFLAGS"] = f"-Dpthread_cancel(x)=0 {env.get('CFLAGS', '')}".strip()
    run([VENV_PYTHON, "-m", "pip", "install", "pyppmd"], env=env)

    log("Installing Python dependencies from requirements.txt...")
    run([VENV_PYTHON, "-m", "pip", "install", "-r", REQUIREMENTS])


def main():
    if "TERMUX_VERSION" not in os.environ and not os.path.exists("/data/data/com.termux"):
        die("This script must be executed inside Termux.")

    setup_termux_repos_and_packages()
    setup_python_environment()
    log("Setup complete! All native tools and Python modules are installed cleanly.")


if __name__ == "__main__":
    main()
