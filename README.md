# Adobe Hackathon 2025 - Round 1A: PDF Outline Extractor

## Challenge Solution
**Connecting the Dots Through Docs**  
A lightweight PDF processor that extracts structured document outlines (title + H1-H3 headings) with page numbers in JSON format.

## Features
-  **Blazing Fast**: Processes 50-page PDFs in <10 seconds
-  **Accurate Hierarchy**: Detects H1, H2, H3 headings using multi-factor analysis
-  **Compact**: Docker image <200MB with zero external dependencies
-  **Secure**: Runs with non-root privileges and no network access

## Technical Specifications
| Requirement | Implementation |
|-------------|----------------|
| Architecture | AMD64 (x86_64) |
| Max Image Size | 150MB |
| Runtime | CPU-only |
| Network | Fully offline |
| RAM Usage | <1GB |
| Output Format | JSON |

## Installation
1. Build the Docker image:
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor:1.0 .
```
2.Usage
```
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor:1.0
```
3.Output Example

    {
      "title": "Understanding AI",
      "outline": [
      {"level": "H1", "text": "Introduction", "page": 1},
      {"level": "H2", "text": "What is AI?", "page": 2},
      {"level": "H3", "text": "History", "page": 3}
    ]
    }
