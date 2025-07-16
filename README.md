# Integration File Processor (Async)

## Description

Integration File Processor is an asynchronous Python-based tool for automating the processing of JSON files placed in nested folders within an `INPUT/` directory. Each JSON file defines a task type and is processed accordingly, making use of public APIs. The output is stored as a new JSON file and the original file is deleted upon success.

---

## Features

- Processes all `.json` files from nested subfolders under `INPUT/`
- Handles task types:
  - `age`: Predicts age using the Agify API
  - `joke`: Fetches a random joke from the Official Joke API
  - Other: Forwards the original JSON unchanged
- Sends the resulting data to a Postman Echo endpoint
- Writes output JSON files with a suffix and removes originals
- Logs processing info and errors to separate log files

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/KrumYakimov/Integration-File-Processor-Async.git
cd integration_file_processor_async
````

### 2. Create a virtual environment (optional)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env` file

- Create a `.env` file in the project root and define the following variables:
  ```plaintext
  # Logging configuration
  LOG_DIR=<your_log_directory>             # Directory for log files (e.g. logs)
  LOG_TO_CONSOLE=<True|False>              # Whether to print logs to console

  # Scheduler configuration
  PROCESS_TIME=<HH:MM>                     # Time of day to trigger processing (e.g. 18:10)


---

## Usage

Usage
- Create the INPUT/ directory in the root folder.

- Place one or more subdirectories inside, each containing .json task files.

- Run the processor:

```bash
python main.py
```

This will process all `.json` files immediately and exit after completion.

---

## Scheduled Execution Options

### Option 1: Run long-running scheduler

```bash
python run_scheduler.py
```

This script runs continuously in the background and triggers processing once per day at the time specified in `.env` (`PROCESS_TIME`).

To keep it running after closing the terminal:

```bash
nohup python run_scheduler.py &
```

### Option 2: Schedule via cron (Linux/macOS)

Edit your crontab:

```bash
crontab -e
```

Add a line (adjust the time and paths as needed):

```cron
10 18 * * * /path/to/venv/bin/python /path/to/integration_file_processor_async/main.py >> /path/to/logs/scheduler.log 2>&1
```

### Option 3: Windows Task Scheduler

Create a daily task with:

* Trigger: Daily at `18:10`
* Action: `python path\to\run_scheduler.py`

---

## Example Input

```json
{
  "name": "Maria",
  "type": "<task_type>",
  "country": "BG"
}
```

---

## Logs

* `logs/info.log`: records processing time and status for each file
* `logs/error.log`: records any encountered errors

---

## Running Tests

Run all tests:

```bash
pytest
```

Run specific test types (with markers):

```bash
pytest -m "unit"
pytest -m "integration"
```

---


