# Google Image Scraper

A simple and efficient command-line tool to download images from Google Images using Python. This script allows you to quickly gather images for your machine learning, computer vision, or any other project that requires image datasets.

## Features

- Download multiple images with a single command
- Supports custom download directory
- Multi-threaded downloads for improved performance
- Automatic file type detection
- Progress bar for download tracking
- Cross-platform support (Windows, Linux, macOS)

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rudzz1950/Web-scraper.git
   cd Web-scraper
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```bash
python scraper.py "search query"
```

### Options

- `-c, --count`: Number of images to download (default: 10)
- `-d, --directory`: Directory to save downloaded images (default: Downloads/google-image-scraper/)
- `-t, --threads`: Number of download threads to use (default: 4)

### Examples

1. Download 20 images of cats:
   ```bash
   python scraper.py "cats" -c 20
   ```

2. Download 50 images of dogs to a custom directory:
   ```bash
   python scraper.py "dogs" -c 50 -d /path/to/save/directory
   ```

3. Use 8 threads for faster downloads:
   ```bash
   python scraper.py "mountains" -c 30 -t 8
   ```

## Output

Downloaded images will be saved in the following structure:
```
<download_directory>/
└── <search_query>/
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

## Dependencies

- requests - For making HTTP requests
- tqdm - For progress bars
- filetype - For file type detection

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and terms of service of the websites you're scraping. The developers are not responsible for any misuse of this tool.
