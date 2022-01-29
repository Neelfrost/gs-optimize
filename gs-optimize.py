import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4

# Ghostscript args
GS_ARGS = (
    "gswin64.exe",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.5",
    "-dNOPAUSE",
    "-dQUIET",
    "-dBATCH",
    "-dPrinted=false",
    "-dSubsetFonts=true",
    "-dCompressFonts=true",
    "-dEmbedAllFonts=true",
    "-dDetectDuplicateImages=true",
    "-dColorImageDownsampleType=/Bicubic",
    "-dColorImageResolution=300",
    "-dGrayImageDownsampleType=/Bicubic",
    "-dGrayImageResolution=300",
    "-dMonoImageDownsampleType=/Bicubic",
    "-dMonoImageResolution=300",
    "-dDownsampleColorImages=true",
    "-sProcessColorModel=DeviceRGB",
    "-sColorConversionStrategy=RGB",
    "-sColorConversionStrategyForImages=RGB",
    "-dConvertCMYKImagesToRGB=true",
    "-sOutputFile=",
)
GS = " ".join(GS_ARGS)


def clear_print(content, next=False):
    """Print on the same line

    Args:
        content (str): content to be printed
        next (bool, default False): if True, continue on next line
    """
    print("\x1b[1K\r" + content, end="" if not next else "\n")


def launch_minimized_process(cmd):
    """Launch a minimized process

    Args:
        cmd (str): complete process command with args

    Returns:
        subprocess.Popen: minimized process

    """
    SW_HIDE = 0
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_HIDE

    return subprocess.Popen(cmd, startupinfo=info)


def convert_from_bytes(bytes):
    """Convert bytes to higher orders

    Args:
        bytes (int): size in bytes
    Returns:
        str: size in higher order
    """
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if bytes < 1000:
            return f"{bytes:.2f} {unit}"
        bytes /= 1000


def unique_filename(ext, prefix=""):
    """Generate a unique file name using uuid4

    Args:
        ext (str): extension of the file
        prefix (str, optional): prefix for the file

    Returns:
        str: unique file name

    """
    return f"{prefix} {uuid4().hex} .{ext}"


def optimize_file(source_file_path, verbose=False):
    """Optimize a pdf

    Args:
        source_file_path (str): path to pdf
        verbose (bool, default False): if True, print compression result

    Returns:
        tuple(int, int): file size before compression, file size after compression
    """
    # Exit if not a pdf
    if not source_file_path.endswith(".pdf"):
        sys.exit("Not a PDF file.")

    source_file_name = os.path.basename(source_file_path)
    source_file_dir = os.path.dirname(source_file_path)
    source_file_size = os.path.getsize(source_file_path)

    # Create optimized pdf with name "temp.pdf"
    output_file_path = os.path.join(source_file_dir, unique_filename("pdf", "temp_"))

    # Spawn process to compress pdf
    process = launch_minimized_process(f'{GS}"{output_file_path}" "{source_file_path}"')
    clear_print(f"Optimizing {source_file_name}...")

    # Wait 60s for process to complete
    # Terminate if not
    try:
        process.wait(60)
    except subprocess.TimeoutExpired:
        process.terminate()

    # Process failed
    if not process.returncode == 0:
        return

    # Process completed without errors
    output_file_size = os.path.getsize(output_file_path)

    # If optimized pdf is smaller than source, replace source
    # Else remove optimized pdf
    if output_file_size < source_file_size:
        # Remove original pdf
        os.remove(source_file_path)

        # Rename optimized pdf
        os.rename(output_file_path, source_file_path)

        # Print result
        if verbose:
            clear_print(
                f"{source_file_name}: "
                f"{convert_from_bytes(source_file_size)} ->"
                f" {convert_from_bytes(output_file_size)}",
                next=True,
            )

        return source_file_size, output_file_size
    else:
        if verbose:
            clear_print(f"{source_file_name}: no optimization needed", next=True)

        # Remove optimized pdf
        os.remove(output_file_path)

        return


def optimize_folder(source_folder_path, verbose=False):
    """Optimize all pdfs within a folder

    Args:
        source_folder_path (str): path to folder
        verbose (bool, default False): if True, print individual compression results
    """
    total_initial_size = 0
    total_final_size = 0

    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Loop over source_folder_path
        for file in os.listdir(source_folder_path):
            # Ignore files starting with temp
            if not file.startswith("temp_") and file.endswith(".pdf"):
                file_path = os.path.join(source_folder_path, file)
                futures.append(executor.submit(optimize_file, file_path, verbose))

    # Obtain total file sizes from future results
    for future in as_completed(futures):
        result = future.result()

        # When optimized pdf is larger than source, nothing is returned
        if not result:
            continue

        total_initial_size += result[0]
        total_final_size += result[1]

    # Print summary
    clear_print("Final compression stats:", next=True)
    clear_print(
        f"{convert_from_bytes(total_initial_size)} ->"
        f" {convert_from_bytes(total_final_size)},"
        f" Compression ratio = {100 * (1 - total_final_size / total_initial_size):.2f}%",
        next=True,
    )


def create_parser():
    """Create CLI parser using argparse

    Returns:
        argparse.Namespace: args
    """
    # Init parser
    parser = argparse.ArgumentParser(
        description="Optimize PDF(s) using Ghostscript. Overwrites original file(s).",
    )

    # Add args
    parser.add_argument(
        "src",
        type=str,
        nargs="+",
        help="path of PDF or folder containing PDFs to be optimized",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="also print compression result of each individual PDF when operating on a folder",
        action="store_true",
    )

    # If no positional arguments are given, print help.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


if __name__ == "__main__":
    args = create_parser()

    for item in args.src:
        if item == ".":
            optimize_file(os.getcwd(), verbose=args.verbose)
        elif os.path.isdir(item):
            optimize_folder(item, verbose=args.verbose)
        elif os.path.isfile(item):
            optimize_file(item, verbose=True)
        else:
            sys.exit("Not a valid path to PDF or folder containing PDFs.")
