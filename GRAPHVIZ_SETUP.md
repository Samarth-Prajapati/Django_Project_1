# Graphviz Setup Instructions

## For Windows

### Option 1: Using winget (Recommended for Windows 10/11)

```bash
winget install graphviz
```

### Option 2: Manual Installation

1. Go to https://graphviz.org/download/
2. Download the Windows installer
3. Install Graphviz
4. Add Graphviz to your PATH:
   - Open System Properties → Advanced → Environment Variables
   - Add the Graphviz bin directory to PATH (usually `C:\Program Files\Graphviz\bin`)

### Option 3: Using Chocolatey

```bash
choco install graphviz
```

## For macOS

```bash
brew install graphviz
```

## For Linux (Ubuntu/Debian)

```bash
sudo apt-get install graphviz
```

## For Linux (CentOS/RHEL)

```bash
sudo yum install graphviz
```

## Verification

After installation, verify Graphviz is working:

```bash
dot -V
```

## Alternative: HTML Tree View

If you can't install Graphviz, use the HTML tree view instead:

- Navigate to `/project-tree-html/` for a simple HTML-based tree visualization
- This doesn't require Graphviz and works in any browser

## Troubleshooting

### Error: "graphviz executables not found"

- Make sure Graphviz is installed system-wide, not just the Python package
- Restart your terminal/command prompt after installation
- Check that `dot` command is available in PATH

### Error: "No module named 'graphviz'"

```bash
pip install graphviz
```

### Error: "Permission denied"

- Run installation as administrator (Windows) or with sudo (Linux/macOS)
