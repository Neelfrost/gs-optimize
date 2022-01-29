<h1 align="center">
    <img
        src="https://raw.githubusercontent.com/Neelfrost/github-assets/main/gs-optimize/logo.png"
        alt="gs-optimize logo"
        width="192"
    />
    <br />
    gs-optimize
</h1>

<p align="center">
    <b>A simple python wrapper to optimize PDFs using Ghostscript.</b><br />
    Compresses PDF to the greatest extent possible with little loss in quality.
</p>

<video src="https://user-images.githubusercontent.com/64243795/151647333-4398808e-ef03-4d77-abc3-4a99cac20c4e.mp4" width="100%"></video>

## Installation

Install dependencies (requires [chocolatey](https://chocolatey.org/install), admin prompt):

```powershell
choco install Ghostscript.app -y;
# Add gswin64.exe to environment path:
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name path -Value $((Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name path).path + ";" + "C:\Program Files\gs\gs<version>\bin" + ";"); exit
```

Clone repo:

```powershell
git clone https://github.com/Neelfrost/gs-optimize.git; cd .\gs-optimize
```

## Usage

```powershell
py .\gs-optimize.py
```

```powershell
usage: gs-optimize.py [-h] [-v] src [src ...]

Optimize PDF(s) using Ghostscript. Overwrites original file(s).

positional arguments:
  src            path of PDF or folder containing PDFs to be optimized

options:
  -h, --help     show this help message and exit
  -v, --verbose  also print compression result of each individual PDF when operating on a folder
```

## TODO

- [ ] Add option for configuring number of threads
- [ ] Add more options
