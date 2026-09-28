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
git clone https://github.com/MysticGSI/mysticgsi.git && cd mysticgsi
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
<summary>macOS Apple Silicon</summary>

```sh
xcode-select --install
brew install python@3.13 cmake ninja pkgconf erofs-utils brotli lz4 \
    pcre2 libusb zstd protobuf aria2 apktool gpatch openssl@3
"$(brew --prefix python@3.13)/bin/python3.13" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/build_android_tools.py
```

</details>

<details>
<summary>Ubuntu / Debian</summary>

```sh
sudo apt-get install python3 python3-venv erofs-utils aria2 patch \
    default-jre-headless curl build-essential cmake ninja-build pkg-config \
    perl golang-go libgtest-dev libusb-1.0-0-dev libpcre2-dev \
    libprotobuf-dev protobuf-compiler libbrotli-dev liblz4-dev libzstd-dev \
    libarchive-tools openssl
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/build_android_tools.py
```

Then install [apktool](#apktool-on-linux).

</details>

<details>
<summary>Arch</summary>

```sh
sudo pacman -Syu --needed python erofs-utils aria2 patch \
    jre-openjdk-headless android-tools curl openssl
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Then install [apktool](#apktool-on-linux), or `android-apktool-bin` from the AUR
(it needs `jre-openjdk` in place of `jre-openjdk-headless`).

</details>

<details>
<summary>NixOS</summary>

```sh
nix develop
python3 cli.py build <name> <firmware> --type <type>
```

</details>

#### apktool on Linux

Grab the latest `apktool_<version>.jar` from the
[releases](https://github.com/iBotPeaches/Apktool/releases):

```sh
mkdir -p ~/.local/bin
curl -fL -o ~/.local/bin/apktool.jar \
    https://github.com/iBotPeaches/Apktool/releases/download/v<version>/apktool_<version>.jar
printf '#!/bin/sh\nexec java -jar "$HOME/.local/bin/apktool.jar" "$@"\n' \
    > ~/.local/bin/apktool
chmod +x ~/.local/bin/apktool
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

```sh
.venv/bin/python cli.py build <name> <firmware or URL> --type <type> [--compress] [--avb-key /path/to/key.pem] [--add <tag>]
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
--type <type> - Type of the ROM to build (alos, hyperos, coloros, oneui, pixel, ...)
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
