# Doujinshi Colorization Manager

This project is a GUI application to manage doujinshi colorization projects, including tracking doujinshi metadata, colorization attempts, and tools used. All functionality is contained in a single `tracker.py` file.

## Project Structure
project/
├── db/                    # Database folder (contains schema and database)
│   ├── schema.sql         # SQL script to initialize the database
│   └── tracker.db         # SQLite database (not tracked, create using schema.sql)
├── doujinshi_collection/  # Folder for doujinshi files (contents not tracked)
├── tracker.py             # Main application script with all functionality
├── .gitignore
└── README.md              # This file

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/AndreOliveiraMendes/doujinshi-tracker.git
cd doujinshi-tracker
```
### 2. Set Up the Database
- Create the db/ folder if it doesn’t exist
```bash
mkdir -p db
```
- Create the SQLite database file db/tracker.db and initialize it with the schema:
```bash
sqlite3 db/tracker.db < db/schema.sql
```
- This will create the necessary tables (color_subject, color_attempt, color_tool).
### 3. Run the Application
- Ensure you have Python 3 and Tkinter installed.
- Run the app:
```bash
python tracker.py
```
### Notes
- The doujinshi_collection/ folder is tracked as an empty directory. Add your doujinshi files locally as needed.
- The db/tracker.db file is not tracked to keep your data private. Use the db/schema.sql script to set it up.