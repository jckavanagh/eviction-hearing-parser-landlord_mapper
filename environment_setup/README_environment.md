# Environment Setup Instructions

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
