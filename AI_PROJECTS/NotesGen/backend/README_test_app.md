# Image Retrieval Test App

A standalone test application to query and retrieve images from the NotesGen database.

## Features

- Test database connection and show basic statistics
- List all PPT files with slide counts and cache status
- List all slides for a specific PPT file with metadata
- Retrieve and display detailed information about specific slide images
- Save slide images (full size or thumbnails) to files
- Verify image integrity using PIL

## Requirements

Install the required dependencies:

```bash
pip install -r test_requirements.txt
```

Or install individually:
```bash
pip install Pillow sqlalchemy pydantic-settings
```

## Usage

### 1. Test Database Connection

```bash
python test_image_retrieval.py --test-connection
```

This will:
- Test the database connection
- Show available tables
- Display count of PPT files and slide images

### 2. List All PPT Files

```bash
python test_image_retrieval.py --list-files
```

This will show:
- PPT file ID, filename, creation date
- Number of slides for each file
- Cache status (whether images are cached)

### 3. List Slides for a Specific PPT File

```bash
python test_image_retrieval.py --list-slides --ppt-id 1
```

This will show all slides for PPT file ID 1:
- Slide numbers
- Image sizes in KB
- Dimensions (width x height)
- Image format (PNG, JPEG, etc.)
- Whether thumbnails are available

### 4. Get Information About a Specific Image

```bash
python test_image_retrieval.py --get-image --ppt-id 1 --slide 1
```

This will display detailed information about slide 1 from PPT file ID 1:
- Image metadata (size, dimensions, format)
- Creation timestamp
- PIL analysis (format, mode, transparency)

### 5. Save an Image to File

```bash
# Save full-size image
python test_image_retrieval.py --save-image --ppt-id 1 --slide 1

# Save thumbnail (if available)
python test_image_retrieval.py --save-image --ppt-id 1 --slide 1 --thumbnail

# Save to custom directory
python test_image_retrieval.py --save-image --ppt-id 1 --slide 1 --output-dir my_images
```

This will:
- Save the image to a file with a descriptive name
- Create the output directory if it doesn't exist
- Show image metadata and verification info
- Verify the image can be opened with PIL

## Example Workflow

1. **Start by testing the connection:**
   ```bash
   python test_image_retrieval.py --test-connection
   ```

2. **List available PPT files:**
   ```bash
   python test_image_retrieval.py --list-files
   ```

3. **Choose a PPT file and list its slides:**
   ```bash
   python test_image_retrieval.py --list-slides --ppt-id 1
   ```

4. **Get detailed info about a specific slide:**
   ```bash
   python test_image_retrieval.py --get-image --ppt-id 1 --slide 1
   ```

5. **Save the image:**
   ```bash
   python test_image_retrieval.py --save-image --ppt-id 1 --slide 1
   ```

## Output

- Images are saved with descriptive filenames: `{ppt_name}_slide_{number}.{format}`
- Thumbnails get a `_thumb` suffix: `{ppt_name}_slide_{number}_thumb.{format}`
- Default output directory is `retrieved_images/`

## Error Handling

The app includes comprehensive error handling and will:
- Show clear error messages for missing files or slides
- Validate command-line arguments
- Handle database connection issues gracefully
- Log detailed error information for debugging

## Database

The app uses the same database configuration as the main NotesGen application:
- Reads settings from `app/core/config.py`
- Uses SQLite by default (`notesgen.db`)
- Supports PostgreSQL if `DATABASE_URL` environment variable is set

## Troubleshooting

### "No module named 'app.database'" Error

This error indicates import path issues. The app should be run from the `backend/` directory:

```bash
cd backend
python test_image_retrieval.py --test-connection
```

### "No PPT files found" Message

This means the database is empty or the connection failed. Check:
- Database file exists (`notesgen.db`)
- Database has been initialized with the correct schema
- Run the test connection command first

### PIL/Image Errors

If PIL cannot open saved images:
- The image data might be corrupted in the database
- The image format might not be supported
- Check the image format field in the database

## Sample Output

```
$ python test_image_retrieval.py --list-files

=== PPT Files in Database ===
ID   Filename                                 Slides   Cached   Created
--------------------------------------------------------------------------------
1    sample_presentation.pptx                 10       Yes      2024-01-15 14:30
2    lecture_slides.pptx                      25       Yes      2024-01-15 15:45

Total files: 2

$ python test_image_retrieval.py --save-image --ppt-id 1 --slide 1

=== Image Saved ===
File: retrieved_images/sample_presentation_slide_01.png
Size: 245.6 KB
Dimensions: 1280x720
Format: PNG
Type: Full Image
PIL Format: PNG
PIL Mode: RGBA
PIL Size: (1280, 720)
✓ Image saved successfully
``` 