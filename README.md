# RakijaGSI

A tool to build a GSI from stock firmware (brought to you by The Balkan People)

Supported firmware: 
- full OTA zips (`payload.bin`)  
- fastboot packages  
- `super.img`, sparse images  
- `system.new.dat`  
- Samsung tars  
- Huawei `UPDATE.APP`  
- Unisoc `.pac`  
- LG `.kdz`  
- Oppo `.ozip`  
- QFIL packages  
- Sony `.sin`  
- Pixel factory images  

Partitions can be ext4, EROFS or F2FS.

## Setup

This project requires Python 3.10+.

On macOS, install Homebrew and Xcode Command Line Tools first.

Sidenote: Homebrew only supports Apple Silicon Macs.
For Intel Macs use MacPorts instead.

### Automatic setup

```sh
git clone https://github.com/Stephanizgo/RakijaGSI.git && cd RakijaGSI
./setup_host.py     # --dev also installs pytest and Ruff
```

The script installs the system packages, creates `.venv` and makes sure
`mke2fs.android` and `e2fsdroid` are available (building them if needed).

### Manual setup

Swap `requirements.txt` for `requirements-dev.txt` if you want the dev tools.

## Prerequisites (Intel-based Macs)

> [!NOTE]  
> Homebrew no longer provides pre-compiled binaries (bottles) for Intel Macs. Using Homebrew will force packages like `protobuf`, `cmake`, and `python` to compile entirely from source, which takes hours and frequently crashes. 
> 
> For Intel Macs, **MacPorts** must be used instead to safely pull pre-compiled Intel binaries.

### 1. Install System Development Tools
Open your terminal and install the required Apple command-line build tools:
```bash
xcode-select --install
```

### 2. Install MacPorts
Go to the official [MacPorts Website](https://macports.org) and download/run the installer package (`.pkg`) for your specific macOS version.

### 3. Configure Your Shell Environment Path
MacPorts installs binaries to `/opt/local/bin`. You must tell your terminal where to find it. Add it to your shell configuration profile:

**For Zsh (Default on macOS Catalina and newer):**
```bash
echo 'export PATH="/opt/local/bin:/opt/local/sbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For Bash (Older macOS versions):**
```bash
echo 'export PATH="/opt/local/bin:/opt/local/sbin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```
Verify the installation by running `port version`.

### 4. Install Project Dependencies
Run the following commands to update MacPorts and fetch all required building binaries:
```bash
sudo port selfupdate
sudo port install python313 cmake ninja pkgconfig erofs-utils brotli lz4 \
    pcre2 libusb-compat zstd protobuf3-cpp aria2 apktool gpatch openssl3
```

---

## Setting Up and Building RakijaGSI

Once your system dependencies are installed via MacPorts, follow these steps to build the toolkit environment and launch the script:

```bash
# 1. Expose GNU patch as "patch" to prevent script errors
export PATH="/opt/local/libexec/gnubin:\$PATH"

# 2. Build the Python virtual environment using MacPorts Python 3.13
/opt/local/bin/python3.13 -m venv .venv

# 3. Install Python dependencies
.venv/bin/python -m pip install -r requirements.txt

# 4. Compile the core Android tools binaries
.venv/bin/python tools/build_android_tools.py
```



<details>
<summary><b>Standard Installation Methods (macOS Apple Silicon)</b></summary>

### For Macs with M1, M2, M3, or M4 chips

1. **Install Apple Developer Tools:** Open your Terminal, paste this command, and press Enter. Follow the pop-up prompts to install it:
   ```sh
   xcode-select --install
   ```

2. **Install Required Packages:** Copy and paste this entire block to install all the tools via Homebrew:
   ```sh
   brew install python@3.13 cmake ninja pkgconf erofs-utils brotli lz4 \
       pcre2 libusb zstd protobuf aria2 apktool gpatch openssl@3
   ```

3. **Create the Python Virtual Environment:** This creates a isolated sandbox folder named `.venv` for the project:
   ```sh
   "\$(brew --prefix python@3.13)/bin/python3.13" -m venv .venv
   ```

4. **Install Python Dependencies:** This installs the internal Python packages required by the builder:
   ```sh
   .venv/bin/python -m pip install -r requirements.txt
   ```

5. **Build Core Android Tools:** Finally, compile the layout tools to finish setup:
   ```sh
   .venv/bin/python tools/build_android_tools.py
   ```
   
</details>

<details>
<summary><b>Standard Installation Methods (Ubuntu / Debian Linux)</b></summary>

### For Ubuntu, Debian, Linux Mint, and WSL2

1. **Install System Dependencies:** Copy and paste this command into your terminal to install all required framework tools, compiler engines, and system libraries. You will be prompted to type your system password:
   ```sh
   sudo apt-get update && sudo apt-get install -y python3 python3-venv erofs-utils aria2 patch \
       default-jre-headless curl build-essential cmake ninja-build pkg-config \
       perl golang-go libgtest-dev libusb-1.0-0-dev libpcre2-dev \
       libprotobuf-dev protobuf-compiler libbrotli-dev liblz4-dev libzstd-dev \
       libarchive-tools openssl
   ```

2. **Create the Python Virtual Environment:** This sets up an isolated Python sandbox folder named `.venv` so the project's scripts don't conflict with your global system files:
   ```sh
   python3 -m venv .venv
   ```

3. **Install Python Libraries:** This updates your environment and downloads the specific packages required by the builder script:
   ```sh
   .venv/bin/python -m pip install -r requirements.txt
   ```

4. **Build Core Android Tools:** Compile the foundational terminal tools to prepare the architecture layout:
   ```sh
   .venv/bin/python tools/build_android_tools.py
   ```

5. **Final Step:** Linux systems require manual installation of `apktool`. Proceed down to the **[apktool on Linux](#apktool-on-linux)** section below to finish your setup.

</details>

<details>
<summary><b>Standard Installation Methods (Arch Linux)</b></summary>

### For Arch Linux, EndeavourOS, and Manjaro

1. **Update and Install Packages:** Run this command to update your system repository and install the core build packages. The `--needed` flag safely ensures you only download tools your computer doesn't already have:
   ```sh
   sudo pacman -Syu --needed python erofs-utils aria2 patch \
       jre-openjdk-headless android-tools curl openssl
   ```

2. **Create the Python Virtual Environment:** Set up your isolated project sandbox folder named `.venv`:
   ```sh
   python -m venv .venv
   ```

3. **Install Python Modules:** Download and configure the specific scripts needed for the GSI toolkit layout:
   ```sh
   .venv/bin/python -m pip install -r requirements.txt
   ```

4. **Install apktool (Required):** You have two easy paths to get `apktool` on Arch:
   * **Option A (Manual):** Leave your system packages as they are and proceed down to the **[apktool on Linux](#apktool-on-linux)** section below.
   * **Option B (AUR):** If you prefer using an AUR helper (like `yay` or `paru`), you can install `android-apktool-bin`. *Note: If you choose this option, you must first swap your headless Java for standard Java by running:*
     ```sh
     sudo pacman -S jre-openjdk
     yay -S android-apktool-bin
     ```
</details>


#### apktool on Linux

If you are using **Ubuntu or Debian**, you can install it simply by running:
```sh
sudo apt install -y apktool
```

Otherwise, copy and paste this automated block into your terminal. It automatically finds the **latest version**, downloads everything, sets up the permissions, and moves it to a folder that your system already knows how to run:

```sh
# 1. Automatically fetch the latest version code from GitHub
APKTOOL_VER=$(curl -s "https://api.github.com/repos/iBotPeaches/Apktool/releases/latest" | grep -Po '"tag_name": "v\K[0-9.]+')

# 2. Download the official Linux runner script directly into your system binary folder
sudo curl -o /usr/local/bin/apktool https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool

# 3. Download the actual executable package matching the latest version
sudo curl -Lo /usr/local/bin/apktool.jar "https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_\${APKTOOL_VER}.jar"

# 4. Give both files permission to run on your computer
sudo chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar
```

To verify that it works perfectly, type `apktool --version` into your terminal.

## Usage

```sh
.venv/bin/python cli.py build <name> <firmware|URL> [--type <type>] [--compress]
.venv/bin/python cli.py rebuild <name> [--compress]
.venv/bin/python cli.py list
.venv/bin/python cli.py clean
```

### Commands

```sh
build - Build a new ROM image
rebuild - Rebuild an existing ROM image
list - List all builds
clean - Clean up all builds
```

### Command-line options

```sh
name - Name of the build
firmware or URL - Path to the firmware or URL to download it from
--type <type> - ROM type; default is auto (use an explicit type if detection fails)
--compress - Compress the output image into a ZIP
--add <tag> - Add a tag to the build name
--no-debloat - Keep the apps the patch set would otherwise remove
--avb-key /path/to/key.pem - Sign with the specified RSA private key
```

By default, an image is signed with AOSP's AVB RSA-2048 test key. You can pass `--avb-key /path/to/key.pem` to sign with your own RSA private key.

Example:

```sh
.venv/bin/python cli.py build raven \
    https://dl.google.com/dl/android/aosp/raven-up1a.231105.003-factory-76a795d5.zip \
    --type pixel --compress
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

```sh
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check .
```

Patch files of 50 MiB or more are stored xz-compressed (`<name>.xz`) and unpacked during builds. After adding one, run `./tools/assets.py pack` and commit the `.xz` files (or `.xz.000`, `.xz.001`, ... for split archives).  

`./tools/assets.py status` shows what's packed.

## License

Apache License 2.0, see [LICENSE](LICENSE). Bundled avbtool is MIT-licensed;
see [tools/avb/LICENSE](tools/avb/LICENSE). Third-party files under `patches/`
have separate terms; see [NOTICE](NOTICE).
