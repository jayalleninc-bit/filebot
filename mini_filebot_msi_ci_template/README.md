# MiniFileBot MSI Builder
This template builds a **Windows MSI installer** for MiniFileBot (FileBot-style GUI).

## Cloud build (recommended)
1. Create a new repo on GitHub, upload this folder contents.
2. Go to **Actions** → run **Build Windows MSI**.
3. Download the artifact; you'll get `MiniFileBot-Installer.msi` (plus the EXE and config).

## Local build (optional)
- Build EXE: use PyInstaller (see previous kits)  
- Build MSI: run `installer\build_msi_local.bat` (installs WiX via Chocolatey if needed).

The MSI installs into `C:\Program Files\MiniFileBot`, creates a Start Menu shortcut, and includes `config.yaml` next to the EXE.
