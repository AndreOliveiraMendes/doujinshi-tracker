-- schema.sql
-- Create the color_subject table
CREATE TABLE IF NOT EXISTS color_subject (
    series_id INTEGER NOT NULL,
    part_id INTEGER,
    code INTEGER NOT NULL PRIMARY KEY,
    series_name TEXT NOT NULL,
    series_alt_name TEXT,
    part_name TEXT,
    part_alt_name TEXT,
    origin TEXT,
    artist TEXT,
    tags TEXT,
    folder_path TEXT NOT NULL
);

-- Create the color_tool table
CREATE TABLE IF NOT EXISTS color_tool (
    tool_id INTEGER PRIMARY KEY,
    tool_name TEXT NOT NULL,
    tool_url TEXT
);

-- Create the color_attempt table
CREATE TABLE IF NOT EXISTS color_attempt (
    code INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    attempt_folder_path TEXT NOT NULL,
    attempt_color_status TEXT NOT NULL,
    attempt_notes TEXT,
    PRIMARY KEY (code, tool_id),
    FOREIGN KEY (code) REFERENCES color_subject(code) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES color_tool(tool_id) ON DELETE CASCADE
);