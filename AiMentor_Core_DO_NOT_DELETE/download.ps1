# AiMentor - One-Command Setup for Windows (PowerShell)
# Usage:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\download.ps1
# Optional:  $env:BONSAI_MODEL = "4B"   (default: auto-select 8B for GPU, 4B for CPU)
param(
    [switch]$Reconfigure
)

$ErrorActionPreference = "Stop"

# Model will be auto-selected based on GPU detection unless user overrides
$UserModelOverride = $env:BONSAI_MODEL  # empty = auto-detect
$ReleaseTag = "prism-b9570-0ad1dab"
$WinAssetTag = "prism-b1-0ad1dab"
$BaseUrl = "https://github.com/PrismML-Eng/llama.cpp/releases/download/$ReleaseTag"
$VenvDir = Join-Path $PSScriptRoot "venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
$RequirementsFile = Join-Path $PSScriptRoot "requirements.txt"

# ── Helpers ──

function Refresh-SessionPath {
    $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $user    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $merged  = "$machine;$user;$env:Path"
    $seen = @{}; $unique = @()
    foreach ($p in $merged -split ";") {
        $key = $p.TrimEnd("\").ToLowerInvariant()
        if ($key -and -not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            $unique += $p
        }
    }
    $env:Path = $unique -join ";"
}

function Find-CompatiblePython {
    $pyLauncher = Get-Command py -CommandType Application -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        foreach ($minor in @("3.13", "3.12", "3.11")) {
            try {
                $out = & $pyLauncher.Source "-$minor" --version 2>&1 | Out-String
                if ($out -match "Python (3\.1[1-3])\.\d+") {
                    $resolvedExe = (& $pyLauncher.Source "-$minor" -c "import sys; print(sys.executable)" 2>$null | Out-String).Trim()
                    if ($resolvedExe -and (Test-Path $resolvedExe)) {
                        return @{ Version = $Matches[1]; Path = $resolvedExe }
                    }
                }
            } catch {}
        }
    }
    foreach ($name in @("python3", "python")) {
        foreach ($cmd in @(Get-Command $name -All -ErrorAction SilentlyContinue)) {
            if (-not $cmd.Source -or $cmd.Source -like "*\WindowsApps\*") { continue }
            try {
                $out = & $cmd.Source --version 2>&1 | Out-String
                if ($out -match "Python (3\.1[1-3])\.\d+") {
                    return @{ Version = $Matches[1]; Path = $cmd.Source }
                }
            } catch {}
        }
    }
    return $null
}

Write-Host ""
Write-Host "==========================================="
if ($Reconfigure) {
    Write-Host "   AiMentor - Reconfigure (Windows)"
} else {
    Write-Host "   AiMentor - Full Setup (Windows)"
}
Write-Host "==========================================="
Write-Host ""

# ── 1. Python ──
if (-not $Reconfigure) {
    Write-Host "==> [1/6] Checking Python ..." -ForegroundColor Cyan
    $DetectedPython = Find-CompatiblePython
    if ($DetectedPython) {
        Write-Host "[OK] Python $($DetectedPython.Version) found at $($DetectedPython.Path)" -ForegroundColor Green
    } else {
        Write-Host "==> Installing Python 3.11 via winget ..." -ForegroundColor Cyan
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Write-Host "[ERR] winget not available. Install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
            exit 1
        }
        $prevEAP = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try { winget install -e --id "Python.Python.3.11" --accept-package-agreements --accept-source-agreements } catch {}
        $ErrorActionPreference = $prevEAP
        Refresh-SessionPath
        $DetectedPython = Find-CompatiblePython
        if (-not $DetectedPython) {
            Write-Host "[ERR] Python installation failed. Install manually from https://www.python.org/downloads/" -ForegroundColor Red
            exit 1
        }
    }

    # ── 2. Virtual Environment + Streamlit ──
    Write-Host "==> [2/6] Setting up Python environment ..." -ForegroundColor Cyan
    if (Test-Path $VenvPy) {
        Write-Host "[OK] Virtual environment already exists." -ForegroundColor Green
    } else {
        & $DetectedPython.Path -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERR] Failed to create virtual environment." -ForegroundColor Red
            exit 1
        }
        Write-Host "[OK] Created virtual environment." -ForegroundColor Green
    }

    Write-Host "==> Installing Python dependencies ..." -ForegroundColor Cyan
    & "$VenvPy" -m pip install --upgrade pip -q
    if (Test-Path $RequirementsFile) {
        & "$VenvPy" -m pip install -r $RequirementsFile -q
    } else {
        & "$VenvPy" -m pip install streamlit requests -q
    }
    Write-Host "[OK] Python dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[SKIP] Steps 1-2: Python & venv already set up." -ForegroundColor DarkGray
}

# ── 3. GPU Detection (Unattended) ──
Write-Host "==> [3/6] Hardware Detection ..." -ForegroundColor Cyan

$GpuType = "cpu"
$CudaTag = "12.4"

$HasNvidia = $false
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) { $HasNvidia = $true }
elseif (Test-Path "$env:ProgramFiles\NVIDIA Corporation\NVSMI\nvidia-smi.exe") { $HasNvidia = $true }
elseif (Test-Path "$env:SystemRoot\System32\nvidia-smi.exe") { $HasNvidia = $true }

if ($HasNvidia) {
    Write-Host "[OK] NVIDIA GPU detected -> CUDA" -ForegroundColor Green
    $GpuType = "cuda"
} else {
    $amd = Get-WmiObject Win32_VideoController -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "AMD|Radeon" }
    if ($amd) {
        Write-Host "[OK] AMD GPU detected -> ROCm/HIP" -ForegroundColor Green
        $GpuType = "hip"
    } else {
        Write-Host "[OK] No supported dedicated GPU found -> CPU" -ForegroundColor Yellow
    }
}

# ── Auto-select model size based on hardware ──
if ($UserModelOverride) {
    $BonsaiModel = $UserModelOverride
    Write-Host "[INFO] Using user-specified model: Bonsai-$BonsaiModel" -ForegroundColor Cyan
} elseif ($GpuType -eq "cpu") {
    $BonsaiModel = "4B"
    Write-Host "[INFO] CPU mode -> downloading lighter Bonsai-4B model (faster on CPU)" -ForegroundColor Yellow
} else {
    $BonsaiModel = "8B"
    Write-Host "[INFO] GPU mode -> downloading full Bonsai-8B model" -ForegroundColor Green
}

$ModelFiles = @{
    "8B" = "Ternary-Bonsai-8B-Q2_0.gguf"
    "4B" = "Bonsai-4B.gguf"
}

$ModelUrls = @{
    "8B" = "https://huggingface.co/prism-ml/Ternary-Bonsai-8B-gguf/resolve/main/Ternary-Bonsai-8B-Q2_0.gguf"
    "4B" = "https://huggingface.co/prism-ml/Bonsai-4B-gguf/resolve/main/Bonsai-4B.gguf"
}

if (-not $ModelUrls.ContainsKey($BonsaiModel)) {
    Write-Host "[ERR] Unsupported BONSAI_MODEL '$BonsaiModel'. Supported values: 8B, 4B" -ForegroundColor Red
    exit 1
}

# ── 4. Download llama-server binaries ──
Write-Host "==> [4/6] Downloading llama-server binaries ..." -ForegroundColor Cyan

$WinArch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq [System.Runtime.InteropServices.Architecture]::Arm64) { "arm64" } else { "x64" }

if ($WinArch -eq "arm64" -and $GpuType -ne "cpu") {
    Write-Host "[WARN] $GpuType detected but no ARM64 build available. Falling back to CPU." -ForegroundColor Yellow
    $GpuType = "cpu"
}

$BinDir = Join-Path $PSScriptRoot "bin\$GpuType"
$VersionFile = Join-Path $BinDir ".llama_version"
$NeedsUpdate = $true

if (Test-Path (Join-Path $BinDir "llama-server.exe")) {
    if (Test-Path $VersionFile) {
        if ((Get-Content $VersionFile -Raw).Trim() -eq $ReleaseTag) {
            $NeedsUpdate = $false
        }
    }
}

if (-not $NeedsUpdate) {
    Write-Host "[OK] Binaries ($ReleaseTag) already present in $BinDir" -ForegroundColor Green
} else {
    Write-Host "    Updating/Downloading binaries to $ReleaseTag ..." -ForegroundColor Cyan
    Stop-Process -Name "llama-server" -Force -ErrorAction SilentlyContinue
    if (Test-Path $BinDir) { Remove-Item -Path $BinDir -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    function Extract-Fast($Url, $Dest) {
        $TmpZip = [System.IO.Path]::GetTempFileName() + ".zip"
        $TmpExt = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
        Write-Host "    Downloading $(Split-Path $Url -Leaf) ..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $Url -OutFile $TmpZip -UseBasicParsing
        New-Item -ItemType Directory -Path $TmpExt -Force | Out-Null
        [System.IO.Compression.ZipFile]::ExtractToDirectory($TmpZip, $TmpExt)
        Copy-Item -Path "$TmpExt\*" -Destination $Dest -Recurse -Force
        Remove-Item $TmpExt -Recurse -Force
        Remove-Item $TmpZip -Force
    }

    if ($GpuType -eq "hip") {
        Extract-Fast "$BaseUrl/llama-bin-win-hip-radeon-x64.zip" $BinDir
    } elseif ($GpuType -eq "cuda") {
        Extract-Fast "$BaseUrl/llama-${WinAssetTag}-bin-win-cuda-${CudaTag}-x64.zip" $BinDir
        try { Extract-Fast "$BaseUrl/cudart-llama-bin-win-cuda-${CudaTag}-x64.zip" $BinDir } catch {}
    } elseif ($GpuType -eq "vulkan") {
        Extract-Fast "$BaseUrl/llama-bin-win-cpu-${WinArch}.zip" $BinDir
        Extract-Fast "$BaseUrl/llama-bin-win-vulkan-x64.zip" $BinDir
    } else {
        Extract-Fast "$BaseUrl/llama-bin-win-cpu-${WinArch}.zip" $BinDir
    }
    
    Set-Content -Path $VersionFile -Value $ReleaseTag
    Write-Host "[OK] Binaries extracted and installed to $BinDir" -ForegroundColor Green
}

# Save detected GPU type for help.ps1
Set-Content -Path (Join-Path $PSScriptRoot ".gpu_type") -Value $GpuType

# ── 5. Download GGUF model ──
Write-Host "==> [5/6] Downloading Bonsai-$BonsaiModel model ..." -ForegroundColor Cyan

$ModelDir = Join-Path $PSScriptRoot "models\gguf\$BonsaiModel"
$ModelFile = $ModelFiles[$BonsaiModel]
$ModelPath = Join-Path $ModelDir $ModelFile

if (Test-Path $ModelPath) {
    Write-Host "[OK] Model already present: $ModelFile" -ForegroundColor Green
    # Remove any other gguf files to avoid conflicts
    Get-ChildItem -Path $ModelDir -Filter "*.gguf" | Where-Object { $_.Name -ne $ModelFile } | Remove-Item -Force
} else {
    New-Item -ItemType Directory -Path $ModelDir -Force | Out-Null
    # Remove any other gguf files to avoid conflicts
    Get-ChildItem -Path $ModelDir -Filter "*.gguf" | Remove-Item -Force
    $ModelUrl = $ModelUrls[$BonsaiModel]
    Write-Host "    Downloading from HuggingFace ..." -ForegroundColor Yellow
    Write-Host "    URL: $ModelUrl" -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelPath -UseBasicParsing
        Write-Host "[OK] Model downloaded: $ModelFile" -ForegroundColor Green
    } catch {
        Write-Host "[ERR] Model download failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Save model size for help.ps1
Set-Content -Path (Join-Path $PSScriptRoot ".model_size") -Value $BonsaiModel

# ── 6. Done ──
Write-Host ""
Write-Host "==========================================="
if ($Reconfigure) {
    Write-Host "   Reconfiguration complete!"
} else {
    Write-Host "   Setup complete!"
}
Write-Host "==========================================="
Write-Host ""
Write-Host "  GPU Mode  : $GpuType" -ForegroundColor Cyan
Write-Host "  Model     : Bonsai-$BonsaiModel" -ForegroundColor Cyan
Write-Host "  Binary    : $BinDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To start AiMentor, run:" -ForegroundColor Green
Write-Host "    .\start.bat" -ForegroundColor Green
Write-Host ""
