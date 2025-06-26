# File Search Agent

This agent allows users to upload a file and ask natural language questions about its content using the OpenAI API.

## Features

- File upload (plain text only; other formats not yet supported)
- Natural language Q&A
- Uses OpenAI for language processing
- Handles large files by chunking

## Usage

See `example.py` for a usage example.

## Limitations & Future Work

- Only plain text files are currently supported.
- Future work: Add support for PDF, DOCX, CSV, and other file types using appropriate extraction libraries.
