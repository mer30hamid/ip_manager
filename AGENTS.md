# Agents Guide for IP Manager

## Project Overview

A lightweight IPv4 management system built with Python Flask for managing large IP address lists. The application allows users to ingest, validate, and deduplicate IPv4 addresses against pre-defined target files.

## Tech Stack

- **Backend**: Python 3.x, Flask micro-framework
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **UI Framework**: Bootstrap 5.3 (ArvanCloud CDN)
- **Icons**: Bootstrap Icons (ArvanCloud CDN)
- **Fonts**: Vazirmatn UI (ArvanCloud CDN, RTL support)
- **Data Storage**: Flat `.txt` files in `ips/` directory
- **IP Validation**: Python `ipaddress` module

## Directory Structure

```
ip_manager/
├── app.py                    # Main Flask application
├── start.cmd                 # Windows startup script (python app.py)
├── README.md                 # Project documentation
├── AGENTS.md                 # This file
├── .crush/                   # Crush configuration (not part of app)
├── templates/
│   └── index.html           # Main UI template
└── ips/
    ├── All.txt              # Master IP list (~8.5MB)
    ├── irancell.txt         # Specific sub-list
    ├── rightel.txt          # Specific sub-list
    ├── samantel.txt         # Specific sub-list
    └── selected.txt         # User-selected IP list
```

## Essential Commands

### Development/Execution

```bash
# Install dependencies (if not already installed)
pip install flask

# Run application locally
python app.py

# Start via Windows batch file
start.cmd

# Access the application
http://127.0.0.1:5000
```

### Data Management

Data files are stored as plain text in the `ips/` directory, one IPv4 address per line. Files are automatically created by the application when processing new IPs.

**Supported Input Formats:**
- Single IPv4: `192.168.1.1`
- CIDR notation: `192.168.1.0/24`, `10.0.0.0/8`
- IP:port combinations: `8.8.8.8:53` → automatically converted to `8.8.8.8`
- CSV format: Multiple IPs separated by newlines or commas

## Application Architecture

### Control Flow

The application follows a specific request-response pipeline:

1. **Route Handler**: `@app.route('/', methods=['GET', 'POST'])` in app.py:30
2. **GET Request**: Renders the main UI with current file state
3. **POST Request**:
   - Retrieves selected target file (from URL params or POST data)
   - Accepts IP input via file upload (.txt) or textarea
   - Loads existing IPs from target file into a Python `set`
   - **Normalizes input**: Extracts IP from IP:port strings, handles CIDR ranges
   - Validates each IP using `ipaddress.IPv4Address()`
   - For CIDR ranges: expands and adds all host IPs to the target file
   - Tracks: new IPs (added), duplicates (ignored), invalid entries (flagged), CIDR ranges
   - Saves sorted IP list back to target file
   - Renders results in the UI

### Key Functions

- `normalize_ip_entry(item)` (app.py:10-18): Extracts clean IP from IP:port strings and handles CIDR notation, returns normalized IP string
- `get_existing_ips(filename)` (app.py:20-26): Loads IPs from target file, returns as set
- `save_ips(filename, ip_set)` (app.py:28-36): Writes sorted IPs to target file, creates `ips/` directory if needed

### Data Structure

**Report object** (returned to template):
```python
{
    "error": "Optional error message in Persian",
    "invalid_details": ["invalid1", "invalid2", ...],  # Up to 500 entries
    "added": 0,  # Integer count
    "duplicates": 0,  # Integer count
    "invalid": 0,  # Integer count
    "total": 0,  # Total unique IPs in target file
    "target_file": "filename.txt"
}
```

### New Features (CIDR & IP:Port)

**IP:Port Handling:**
- Automatically extracts IP address from input strings containing ports
- Example: `8.8.8.8:53` → `8.8.8.8`
- Example: `192.168.1.100:8080` → `192.168.1.100`

**CIDR Notation Support:**
- Accepts IPv4 CIDR ranges (e.g., `192.168.1.0/24`, `10.0.0.0/8`)
- Expands CIDR range and adds all host IPs to target file
- Example: `192.168.1.0/24` → adds `192.168.1.1` through `192.168.1.254`
- Counts as a single "duplicate" entry (doesn't add individual IPs to duplicate count)

**Report Object Update:**
- New field: `"cidr_count"` (integer) - number of CIDR ranges processed

## Naming Conventions

### Files
- Target files: lowercase with underscores (e.g., `irancell.txt`, `All.txt`)
- Backend: lowercase snake_case (e.g., `app.py`)
- Templates: lowercase with underscores (e.g., `index.html`)
- Script: lowercase with underscores (e.g., `start.cmd`)

### Code Variables
- Function names: snake_case (e.g., `get_existing_ips`, `save_ips`)
- Variable names: lowercase snake_case (e.g., `input_items`, `ip_set`, `report`)
- Constants: UPPERCASE_SNAKE_CASE (e.g., `ALLOWED_FILES`, `MAX_CONTENT_LENGTH`)

### UI Elements
- IDs: lowercase with hyphens (e.g., `selected-file-input`, `theme-toggle`)
- Classes: kebab-case (e.g., `file-nav-item`, `form-control`)

## Code Patterns

### Error Handling
- Uses try-except blocks with generic exception catching for IP validation errors
- Limits `invalid_list` to 500 entries to prevent memory exhaustion
- Returns structured error reports in Persian language

### File Operations
- Always use `ips/` subdirectory for data storage
- Create directory with `os.makedirs()` if it doesn't exist
- Use UTF-8 encoding for file reading/writing
- Sort IPs alphabetically before writing to file

### URL State Management
- File selection is maintained via URL query param: `?current_file=filename.txt`
- File selection form uses `method="GET"` for navigation
- Main data submission uses `method="POST"` to handle file uploads

## UI Patterns

### RTL Support
- Root HTML element has `dir="rtl"` for Persian language support
- Bootstrap 5.3 theme attribute: `data-bs-theme="light"` or `"dark"`
- Theme state persisted in browser `localStorage`

### File Selector UI
- Segmented control interface using Bootstrap grid/flex
- Visual indicators (icons + filename) for each file
- Active state uses gradient background with hover effects

### Theming
- CSS variables for dynamic theming (dark/light mode)
- Custom scrollbar styling for both themes
- Font switching to Vazirmatn UI for Persian text

## Important Gotchas

### File Upload Limits
- `MAX_CONTENT_LENGTH` set to 100MB in app.py:6
- Required for handling large IP lists (>10K entries)
- Upload file is decoded as UTF-8 text

### Deduplication Logic
- Uses Python `set` for O(1) lookups
- Comparison is exact match (no partial matching)
- Case-sensitive: "192.168.1.1" vs "192.168.1.1" match, but "192.168.1.1" vs "192.168.1.10" are different

### IP Validation
- Uses Python's `ipaddress.IPv4Address()` which strictly enforces IPv4 format
- Rejects IPv6, invalid formats, and malformed addresses
- Returns `InvalidAddress` exception for non-IPv4 strings

### Content Encoding
- CSV-like input: commas are replaced with newlines for parsing
- Both file upload and textarea support comma-separated values
- Whitespace is stripped from each line

### Memory Management
- `invalid_details` limited to 500 entries maximum (app.py:72)
- Entire `existing_ips` set is stored in memory during processing

## Scaling Considerations

**Current Limitations:**
- Flat file storage (no database)
- Single-threaded Flask development server (not production-ready)
- No concurrent access support
- IPv4-only validation

**Potential Improvements:**
- Migrate to SQLite/PostgreSQL for better concurrency
- Add IPv6 validation support (already partially implemented)
- Convert to RESTful API for CLI tools
- **Add CIDR notation support** (IPv4 range support - e.g., `192.168.1.0/24`)
- **Add IP:port handling** (automatically extracts IP from `192.168.1.1:53` to `192.168.1.1`)
- Add file upload size validation
- Implement file locking for concurrent writes

## Development Workflow

1. **Backend Changes**: Modify `app.py` - main Flask routes, logic, and file operations
2. **Frontend Changes**: Edit `templates/index.html` - HTML structure, CSS, and JavaScript
3. **Data Changes**: Add/update `.txt` files in `ips/` directory
4. **Testing**: Start application, test IP ingestion and deduplication
5. **Localization**: All UI text in Persian; maintain language consistency

## Security Notes

- No authentication or authorization implemented
- No CSRF protection
- No input sanitization beyond IP validation
- Runs on development server only (debug mode enabled)
- No database credentials or sensitive configuration

**Do not deploy this application as-is in a production environment without adding:**
- Authentication and authorization
- CSRF protection
- Input validation and sanitization
- Production WSGI server (Gunicorn/uWSGI)
- Environment variable configuration
- HTTPS/SSL