# Multi-Target IPv4 Management System

## 📌 Overview

A lightweight, single-page web application built with **Python (Flask)** designed for efficient management of large IPv4 address lists. The system allows users to ingest IP addresses via manual text input or file uploads, validates them against IPv4 standards, performs deduplication against pre-defined target files, and provides detailed operational reporting.



<img width="1024" height="1355" alt="Screen Shot 2026-05-08 at 13 59 21" src="https://github.com/user-attachments/assets/40fd8993-b6bb-48ea-8cb2-2dc022c34d20" />






## 🛠 Tech Stack

-   **Backend:** Python 3.x, Flask (Micro-framework)
-   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
-   **UI Framework:** Bootstrap 5.3 (via ArvanCloud CDN)
-   **Icons:** Bootstrap Icons (via ArvanCloud CDN)
-   **Fonts:** Vazirmatn UI (via ArvanCloud CDN)
-   **Data Storage:** Flat `.txt` files (serving as lightweight databases)

## 🚀 Core Logic & Workflow

The application follows a specific processing pipeline for every request:

1.  **Target Selection:** The user selects one of the predefined target files via a segmented UI control (`All.txt`, `irancell.txt`, `rightel.txt`, `samantel.txt`, or `selected.txt`). This selection is persisted via URL parameters.
2.  **Data Ingestion:**
    -   **Method A (Large Data):** File upload (.txt) to prevent `Request Entity Too Large` errors.
    -   **Method B (Small Data):** Direct text area input.
3.  **Validation Pipeline:** Every entry is passed through the Python `ipaddress` library to ensure it conforms strictly to **IPv4** standards.
4.  **Deduplication Logic:**
    -   The system loads the existing set of IPs from the selected target file into a Python `set`.
    -   New valid IPs are compared against this set.
    -   If an IP exists, it is flagged as a **Duplicate**.
    -   If an IP does not exist, it is added to the set and marked as **Added**.
5.  **Error Handling:** Non-IPv4 strings are captured in an `invalid_list` for user review via a Bootstrap Modal.
6.  **Persistence:** The updated set of IPs is sorted and written back to the selected `.txt` file.

## 📊 Data Schema & Storage

The system uses flat files as data stores. Each file acts as an independent database:

-   `All.txt`: Master list.
-   `irancell.txt`, `rightel.txt`, etc.: Specific sub-lists.

**File Format:** One IPv4 address per line (e.g., `192.168.1.1`).

## 🤖 AI Context & Development Roadmap

_For LLMs/Developers: Use this section to understand the architectural intent._

### Current Capabilities:

-   **Complexity:** O(N)O(N)O(N) for processing, where NNN is the number of input IPs (due to set lookups being O(1)O(1)O(1)).
-   **Memory Management:** Implemented a limit on `invalid_list` size (500 entries) to prevent memory exhaustion during massive invalid inputs.
-   **State Management:** UI state (Dark/Light mode) is managed via browser `localStorage`.

### Potential Scaling Paths:

1.  **Database Migration:** Transition from `.txt` files to SQLite or PostgreSQL for better ACID compliance and concurrent access.
2.  **IPv6 Support:** Expand the validation logic to include IPv6 addresses.
3.  **API Integration:** Convert the Flask routes into a RESTful API to allow headless management via CLI tools.
4.  **Advanced Filtering:** Implement CIDR notation support (e.g., allowing users to add entire ranges like `192.168.1.0/24`).

## ⚙️ Installation & Local Execution

1.  **Prerequisites:** Python 3.x installed on Windows.
2.  **Install Dependencies:**
    
    bash
    
    ```bash
    pip install flask
    ```
    
3.  **Run Application:**
    
    bash
    
    ```bash
    python app.py
    ```
    
4.  **Access:** Open `http://127.0.0.1:5000` in your preferred web browser.

* * *

**Note:** This application is intended for local use on Windows environments and does not require a production-grade web server (like Gunicorn) due to its lightweight nature
