#!/usr/bin/env bash
# ============================================================
# llm-lite :: Release Installer
# Supports: Ubuntu/Debian, Fedora, Arch, macOS (Homebrew),
#           Raspberry Pi 4/5 (aarch64 Debian)
# Usage:    bash install.sh
# ============================================================
set -euo pipefail

# ─── colors ─────────────────────────────────────────────────
R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'
B='\033[0;34m'; C='\033[0;36m'; W='\033[1;37m'; N='\033[0m'

info()  { echo -e "${C}[INFO]${N}  $*"; }
ok()    { echo -e "${G}[ OK ]${N}  $*"; }
warn()  { echo -e "${Y}[WARN]${N}  $*"; }
die()   { echo -e "${R}[FAIL]${N}  $*" >&2; exit 1; }
hdr()   { echo -e "\n${W}══ $* ══${N}"; }

# ─── detect OS / arch ───────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"
info "OS: $OS  |  Arch: $ARCH"

IS_LINUX=false; IS_MACOS=false; IS_RPI=false
[[ "$OS" == Linux  ]] && IS_LINUX=true
[[ "$OS" == Darwin ]] && IS_MACOS=true

if $IS_LINUX && [[ -f /proc/device-tree/model ]]; then
    grep -qi "raspberry" /proc/device-tree/model 2>/dev/null && IS_RPI=true
fi

# ─── paths ──────────────────────────────────────────────────
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFER_DIR="$INSTALL_DIR/x64/gemma3N_E4B"
NATIVE_DIR="$INSTALL_DIR/native"
VENV_DIR="$INFER_DIR/pynq_env"
WEIGHTS_DIR="$INFER_DIR/local_gemma_3n_int4"
CACHE_DIR="$INFER_DIR/local_gemma_3n_cache"

# HuggingFace model IDs
HF_MODEL_ID="google/gemma-3n-E4B-it"
HF_TOKENIZER_ONLY=true   # set false to download full weights (large)

hdr "llm-lite Installer"
echo -e "  Install path : ${B}$INSTALL_DIR${N}"
echo -e "  Inference dir: ${B}$INFER_DIR${N}"

# ─── 1. system dependencies ─────────────────────────────────
hdr "1/6  System Dependencies"

install_linux_deps() {
    # detect package manager
    if command -v apt-get &>/dev/null; then
        PKG_MGR="apt-get"
        PKG_INSTALL="sudo apt-get install -y"
        PKG_UPDATE="sudo apt-get update -qq"
        PKGS=(
            python3 python3-pip python3-venv python3-dev
            libvulkan-dev vulkan-tools vulkan-validationlayers
            libglfw3-dev cmake build-essential glslang-tools
            git curl wget
        )
        $PKG_UPDATE
        $PKG_INSTALL "${PKGS[@]}"
    elif command -v dnf &>/dev/null; then
        PKG_INSTALL="sudo dnf install -y"
        PKGS=(
            python3 python3-pip python3-devel
            vulkan-loader-devel glfw-devel cmake gcc-c++
            glslang git curl wget
        )
        $PKG_INSTALL "${PKGS[@]}"
    elif command -v pacman &>/dev/null; then
        PKG_INSTALL="sudo pacman -S --noconfirm"
        PKGS=(
            python python-pip
            vulkan-icd-loader vulkan-headers glfw cmake
            glslang git curl wget
        )
        $PKG_INSTALL "${PKGS[@]}"
    else
        warn "Unknown package manager — skipping system deps."
        warn "Ensure these are installed: python3, python3-pip, python3-venv,"
        warn "  libvulkan-dev, libglfw3-dev, cmake, build-essential, glslang-tools"
    fi
}

install_macos_deps() {
    if ! command -v brew &>/dev/null; then
        info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew update
    brew install python3 cmake glfw molten-vk glslang git
    # MoltenVK provides Vulkan on macOS; set env var
    export VK_ICD_FILENAMES="$(brew --prefix molten-vk)/share/vulkan/icd.d/MoltenVK_icd.json"
    info "MoltenVK path: $VK_ICD_FILENAMES"
    echo "export VK_ICD_FILENAMES=\"$VK_ICD_FILENAMES\"" >> "$INSTALL_DIR/.env"
}

if $IS_LINUX;  then install_linux_deps; fi
if $IS_MACOS;  then install_macos_deps; fi

ok "System deps done"

# ─── 2. Python venv ─────────────────────────────────────────
hdr "2/6  Python Virtual Environment"

PYTHON=$(command -v python3 || command -v python || die "python3 not found")
info "Using: $PYTHON $(${PYTHON} --version)"

if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating venv at $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
else
    info "Venv exists, reusing"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet

info "Installing Python packages..."
pip install -r "$INFER_DIR/requirements.txt" --quiet
ok "Python environment ready"

# ─── 3. Model weights ───────────────────────────────────────
hdr "3/6  Model Weights"

mkdir -p "$WEIGHTS_DIR" "$CACHE_DIR"

# Check if weights already present
if ls "$WEIGHTS_DIR"/*.safetensors &>/dev/null 2>&1 || \
   ls "$WEIGHTS_DIR"/*.npy &>/dev/null 2>&1; then
    ok "Weights already present in $WEIGHTS_DIR — skipping download"
else
    info "Downloading tokenizer from HuggingFace: $HF_MODEL_ID"
    info "(Large model weights must be placed manually in $WEIGHTS_DIR)"
    info ""
    info "To download automatically, install huggingface_hub and run:"
    info "  source $VENV_DIR/bin/activate"
    info "  huggingface-cli download $HF_MODEL_ID \\"
    info "    --include 'tokenizer*' 'config*' \\"
    info "    --local-dir $CACHE_DIR"
    info ""
    info "For INT4 quantized weights (recommended):"
    info "  1. Download the original safetensors to a temp dir"
    info "  2. Run: python $INFER_DIR/quantize.py --input <tmpdir> --output $WEIGHTS_DIR"
    info ""

    # Try to download tokenizer files only (small, always needed)
    if python3 -c "import huggingface_hub" 2>/dev/null; then
        info "Attempting tokenizer download..."
        python3 - <<PYEOF
import sys
try:
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id="$HF_MODEL_ID",
        allow_patterns=["tokenizer*", "config.json", "generation_config.json"],
        local_dir="$CACHE_DIR",
        ignore_patterns=["*.safetensors", "*.bin"]
    )
    print("[OK] Tokenizer downloaded")
except Exception as e:
    print(f"[WARN] Could not auto-download: {e}")
    print("       Run: huggingface-cli login  (if model requires auth)")
    sys.exit(0)
PYEOF
    else
        warn "huggingface_hub not available for tokenizer download"
        warn "Install it: pip install huggingface-hub"
    fi
fi

ok "Weights step complete"

# ─── 4. C++ shared libraries ────────────────────────────────
hdr "4/6  Compiling C++ DLLs"

cd "$INFER_DIR"

# Pick march based on arch
case "$ARCH" in
    x86_64)
        # detect znver2 (Ryzen 4xxx/5xxx) vs generic
        if grep -q "znver2\|znver3\|znver4" /proc/cpuinfo 2>/dev/null; then
            MARCH="-march=znver2"
        else
            MARCH="-march=native"
        fi
        ;;
    aarch64)
        MARCH="-march=armv8-a+simd -mfp16-format=ieee"
        ;;
    armv7*)
        MARCH="-march=armv7-a -mfpu=neon-fp-armv8 -mfloat-abi=hard -mfp16-format=ieee"
        ;;
    *)
        MARCH=""
        warn "Unknown arch $ARCH — no -march flag"
        ;;
esac

info "Compiling my_accelerator.so  (SIMD/OpenMP) [$MARCH]"
g++ -O3 $MARCH -shared -fPIC -fopenmp \
    -o C_DLL/my_accelerator.so C_DLL/my_accelerator.cpp
ok "my_accelerator.so"

if pkg-config --exists vulkan 2>/dev/null || \
   [[ -f /usr/include/vulkan/vulkan.h ]] || \
   [[ -f /usr/local/include/vulkan/vulkan.h ]]; then
    info "Compiling vulkan_core.so  (Vulkan compute)"
    g++ -O3 $MARCH -shared -fPIC \
        -o C_DLL/vulkan_core.so C_DLL/vulkan_core.cpp \
        -lvulkan
    ok "vulkan_core.so"

    # Recompile shaders if glslangValidator available
    if command -v glslangValidator &>/dev/null; then
        for shader in C_DLL/gemv_int4.comp C_DLL/gemv_int4_vector4.comp; do
            spv="${shader%.comp}.spv"
            info "Compiling shader: $shader"
            glslangValidator -V "$shader" -o "$spv"
        done
        ok "Shaders compiled"
    else
        info "glslangValidator not found — using pre-built .spv files"
    fi
else
    warn "Vulkan headers not found — skipping vulkan_core.so"
    warn "  Install: sudo apt install libvulkan-dev"
fi

cd "$INSTALL_DIR"
ok "C++ DLLs compiled"

# ─── 5. Native GUI (CMake, DEPRECATED) ───────────────────────
hdr "5/6  Native GUI (deprecated)"

# The Dear ImGui + Vulkan front-end in native/ is no longer the supported
# path — see native/DEPRECATED.md.  We skip it by default; opt-in with
# LLMLITE_BUILD_NATIVE=1 if you still want to build it.
if [[ "${LLMLITE_BUILD_NATIVE:-0}" == "1" ]] && [[ -d "$NATIVE_DIR" ]] && command -v cmake &>/dev/null; then
    info "LLMLITE_BUILD_NATIVE=1 — building anyway..."
    cmake -S "$NATIVE_DIR" -B "$NATIVE_DIR/build" \
        -DCMAKE_BUILD_TYPE=Release \
        -G "Unix Makefiles" --log-level=WARNING 2>&1 | tail -5
    cmake --build "$NATIVE_DIR/build" --parallel "$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)"
    ok "Native GUI built: $NATIVE_DIR/build/llm-lite-native"
else
    info "Skipping native GUI (use the web GUI at http://127.0.0.1:5000 or the CLI)."
fi

# ─── 6. Launcher scripts ────────────────────────────────────
hdr "6/6  Creating Launchers"

# run.sh — web GUI launcher
cat > "$INSTALL_DIR/run.sh" << LAUNCHER
#!/usr/bin/env bash
# llm-lite launcher — starts Python Flask web GUI
set -euo pipefail

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INFER_DIR="\$SCRIPT_DIR/x64/gemma3N_E4B"

# Load optional env (MoltenVK path on macOS, etc.)
[[ -f "\$SCRIPT_DIR/.env" ]] && source "\$SCRIPT_DIR/.env"

source "\$INFER_DIR/pynq_env/bin/activate"
cd "\$INFER_DIR"

echo ""
echo "  llm-lite :: Gemma 3N E4B"
echo "  Web GUI: http://127.0.0.1:5000"
echo "  Press Ctrl+C to stop"
echo ""
python gui_app.py
LAUNCHER
chmod +x "$INSTALL_DIR/run.sh"
ok "run.sh created"

# run-native.sh — native GUI launcher
if [[ -f "$NATIVE_DIR/build/llm-lite-native" ]]; then
    cat > "$INSTALL_DIR/run-native.sh" << NLAUNCHER
#!/usr/bin/env bash
# llm-lite native GUI — starts Flask backend + ImGui GUI
set -euo pipefail

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INFER_DIR="\$SCRIPT_DIR/x64/gemma3N_E4B"
NATIVE="\$SCRIPT_DIR/native/build/llm-lite-native"

[[ -f "\$SCRIPT_DIR/.env" ]] && source "\$SCRIPT_DIR/.env"
source "\$INFER_DIR/pynq_env/bin/activate"

# Start Flask backend in background
cd "\$INFER_DIR"
python gui_app.py &
BACKEND_PID=\$!

# Give backend 2 seconds to start
sleep 2

echo "  Starting native GUI..."
cd "\$INFER_DIR"
"\$NATIVE"

# Kill backend when GUI exits
kill \$BACKEND_PID 2>/dev/null || true
NLAUNCHER
    chmod +x "$INSTALL_DIR/run-native.sh"
    ok "run-native.sh created"
fi

# ─── summary ────────────────────────────────────────────────
echo ""
echo -e "${W}══════════════════════════════════════════${N}"
echo -e "${G}  Installation complete!${N}"
echo -e "${W}══════════════════════════════════════════${N}"
echo ""
echo -e "  Web GUI:     ${C}bash run.sh${N}  (full feature set)"
echo -e "  CLI:         ${C}cd x64/gemma3N_E4B && source pynq_env/bin/activate && python3 main.py${N}"
if [[ -f "$NATIVE_DIR/build/llm-lite-native" ]]; then
echo -e "  Native GUI:  ${C}bash run-native.sh${N}  ${Y}(deprecated)${N}"
fi
echo ""
if ! ls "$WEIGHTS_DIR"/*.safetensors &>/dev/null 2>&1 && \
   ! ls "$WEIGHTS_DIR"/*.npy &>/dev/null 2>&1; then
    echo -e "${Y}  ⚠  Model weights not found in:${N}"
    echo -e "     ${B}$WEIGHTS_DIR${N}"
    echo -e "  Download quantized weights and place them there, then run again."
    echo ""
fi
