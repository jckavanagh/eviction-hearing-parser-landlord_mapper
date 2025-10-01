# LandLord Mapper: Environment Setup Instructions

## 1. Installing ChromeDriver

TASK: from project's root directory, in terminal run either command:

`./environment_setup/install_chromedriver.py`

OR

`python ./envrionment_setup/install_chromedriver.py`

_NOTE: installs in project's root directory a version of ChromeDriver unique to local computer's chrome browser version_

- ✅ Detects Chrome version on macOS, Linux, and Windows
- ✅ Automatically downloads the matching ChromeDriver version
- ✅ Handles both old and new ChromeDriver distribution systems (pre-115 and 115+)
- ✅ Platform detection for Mac (Intel & ARM), Linux, and Windows
- ✅ Extracts and places ChromeDriver in the project root directory
- ✅ Makes it executable on Unix-like systems
- ✅ Checks for existing ChromeDriver and asks before replacing

## 2. Create & Activate Virtual Environment

TASK: from project's root directory, in terminal run commands:

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

## 3A. Set .env variables & connect to Supabase Database

TASK: from project's root directory, in terminal run commands:

`echo "LOCAL_DATABASE_URL=postgresql://[user]:[database_password]@[host]:[port]/postgres" > .env`

`echo "LOCAL_DEV=true" >> .env`

_NOTE: variables for LOCAL_DATABASE_URL can be found via navigating to your Supabase Database's connection string, selecting URI from the Type drop down menu and expanding the View Parameters drop down_

## 3B. [Optional] Test Database Connection

TASK: from project's root directory, in terminal run commands:

`./environment_setup/test_database_connection.py`

TASK: Check Supabase for test_table (via navigation sidebar: Table Editor, Database, etc)
TASK: In terminal prompt 'What would you like to do with test_table?' Enter choice [2] to delete test_table from Database

## 4. Initialize Eviction Parser Tables & Views in Supabase Database

TASK: In Supabase project's SQL Editor **COPY & RUN** full content from `init_supabase.sql` file located in environment_setup folder
