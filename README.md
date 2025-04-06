# Doujinshi Colorization Manager

This project is a GUI application for managing doujinshi colorization projects. It tracks doujinshi metadata, colorization attempts, and the tools used. The functionality is split into the following components:
- The screen folder contains the screen definitions.
- app.py manages the application and screens.
- database.py handles database operations.
- main.py serves as the main entry point.

## Project Structure
```
doujinshi_manager/
├── db/
|   ├── schema.sql            # Your existing schema file
|   ├── tracker.db            # Your existing database file
|
├── doujinshi_collection/     # Your existing directory for doujinshi folders
|
├── screens/                  # Directory for all screen classes
|   ├── utility/              # Utility function for screen classes
|   |   ├── Dinamic_table.py
|   |   └── __init__.py
|   |
|   ├── __init__.py
|   ├── attempt_insert.py
|   ├── attempt_menu.py
|   ├── attempt_modify.py
|   ├── attempt_view.py
|   ├── database_menu.py
|   ├── directory_menu.py
|   ├── doujinshi_insert.py
|   ├── doujinshi_menu.py
|   ├── doujinshi_modify.py
|   ├── doujinshi_view.py
|   ├── main_menu.py
|   ├── tool_insert.py
|   ├── tool_menu.py
|   ├── tool_modify.py
|   └── tool_view.py
|
├── .gitignore
├── README.md
├── app.py                # Main application class (DoujinshiManagerApp)
├── database.py           # Database connection and management
├── main.py               # Entry point to run the app
```
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
python main.py
```
### Notes
- The doujinshi_collection/ folder is tracked as an empty directory. Add your doujinshi files locally as needed.
- The db/tracker.db file is not tracked to keep your data private. Use the db/schema.sql script to set it up.
