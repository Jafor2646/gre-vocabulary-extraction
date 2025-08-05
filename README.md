# GRE Vocabulary Extraction Automation

A Python automation tool that extracts vocabulary words from a source Google Sheet and enriches them with definitions, examples, and synonyms using a free dictionary API, then populates a target Google Sheet for GRE vocabulary study.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Details](#api-details)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This automation script processes vocabulary words from the "Greg Mat Vocab List (37 Groups, 1,110 Words)" Google Sheet and creates a comprehensive vocabulary database with:

- Word definitions
- Parts of speech
- Usage examples
- Synonyms/similar words

The processed data is automatically organized in a target Google Sheet for easy GRE vocabulary study.

## ✨ Features

- **Multi-Range Processing**: Extracts words from specific ranges (A4:S33, A37:S66, A70:S132)
- **Smart Filtering**: Only processes words starting with lowercase letters
- **Duplicate Prevention**: Automatically skips words already processed
- **Error Handling**: Robust handling of API failures and network issues
- **Progress Tracking**: Real-time progress updates with detailed statistics
- **Rate Limiting**: Built-in delays to respect API limits
- **Comprehensive Logging**: Detailed console output for monitoring

## 🔧 Prerequisites

- Python 3.7 or higher
- Google Cloud Platform account
- Google Sheets API enabled
- Service Account with appropriate permissions

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jafor2646/gre-vocabulary-extraction.git
   cd gre-vocabulary-extraction
   ```

2. **Create and activate virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install required packages**:
   ```bash
   pip install gspread oauth2client requests
   ```

## ⚙️ Configuration

### 1. Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Download the JSON credentials file
   - Rename it to match `SERVICE_ACCOUNT_FILE` in the script

### 2. Google Sheets Permissions

Share both Google Sheets with your service account email:

**Source Sheet**: `https://docs.google.com/spreadsheets/d/1jRATLVV34vATsL4Y67fZZXQc7qZPYc0c0Yk7Bykh4fw/edit`
- Permission: Viewer

**Target Sheet**: `https://docs.google.com/spreadsheets/d/15vHs62RjZ8ACfywWWQTr6JMKBe_vJ9JhdZGQVDgIhXE/edit`
- Permission: Editor

### 3. Script Configuration

Update the configuration section in `automation.py`:

```python
# ========== CONFIGURATION ==========
SERVICE_ACCOUNT_FILE = 'your-service-account-file.json'
SOURCE_SHEET_ID = '1jRATLVV34vATsL4Y67fZZXQc7qZPYc0c0Yk7Bykh4fw'
TARGET_SHEET_ID = '15vHs62RjZ8ACfywWWQTr6JMKBe_vJ9JhdZGQVDgIhXE'
TARGET_HEADERS = ['word', 'pos', 'meaning', 'example', 'similar word']
```

## 🚀 Usage

### Basic Usage

Run the automation script:

```powershell
python automation.py
```

### What the Script Does

1. **Connects to Google Sheets**: Opens both source and target sheets
2. **Extracts Words**: Scans specified ranges for vocabulary words
3. **Filters Words**: Only processes words starting with lowercase letters
4. **Checks for Duplicates**: Skips words already in the target sheet
5. **Fetches Definitions**: Uses free dictionary API to get word details
6. **Populates Target Sheet**: Adds enriched vocabulary data

### Expected Output

```
✅ Successfully opened source sheet
✅ Successfully opened target sheet
✅ Target sheet already has headers
🔍 Extracting words from specified ranges...
📍 Processing range 1: Row 4-33, Col A-S
✅ Range 1 processed
📍 Processing range 2: Row 37-66, Col A-S
✅ Range 2 processed
📍 Processing range 3: Row 70-132, Col A-S
✅ Range 3 processed
✅ Found 1110 unique words starting with lowercase letters
📋 Words already in target sheet: 1097
🆕 New words to process: 13

🚀 Starting to process 13 new words...
==================================================
[1/13] Fetching: example_word
✅ Added 'example_word' to sheet
...
==================================================
✅ Processing complete!
📊 Final stats: 13 successful, 0 errors out of 13 total words
📈 Total words now in target sheet: 1110
🔗 Check your target sheet: [Your Sheet URL]
```

## 📁 Project Structure

```
gre-vocabulary-extraction/
├── automation.py              # Main automation script
├── gre-vocab-api-*.json      # Google Service Account credentials (excluded from git)
├── .gitignore                # Git ignore file
├── .venv/                    # Virtual environment (excluded from git)
├── README.md                 # This documentation
└── requirements.txt          # Python dependencies (if created)
```

## 🔌 API Details

### Dictionary API

- **Endpoint**: `https://api.dictionaryapi.dev/api/v2/entries/en/{word}`
- **Method**: GET
- **Rate Limit**: 1 request per second (built into script)
- **Response Format**: JSON
- **Cost**: Free

### Sample API Response

```json
[
  {
    "word": "example",
    "meanings": [
      {
        "partOfSpeech": "noun",
        "definitions": [
          {
            "definition": "a thing characteristic of its kind or illustrating a general rule",
            "example": "it's a good example of how European action can produce results",
            "synonyms": ["specimen", "sample", "instance"]
          }
        ]
      }
    ]
  }
]
```

### Google Sheets API

- **Scopes Used**:
  - `https://spreadsheets.google.com/feeds`
  - `https://www.googleapis.com/auth/drive`
  - `https://www.googleapis.com/auth/spreadsheets`

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Error
```
❌ Error opening sheets: [Errno 13] Permission denied
```
**Solution**: Ensure service account email is shared with both Google Sheets

#### 2. API Rate Limit
```
❌ Network error fetching word 'example': HTTPSConnectionPool timeout
```
**Solution**: The script includes 1-second delays. Network issues are temporary.

#### 3. No Words Found
```
✅ Found 0 unique words starting with lowercase letters
```
**Solution**: Check if the source sheet ranges and filtering criteria are correct

#### 4. Virtual Environment Issues
```powershell
# To deactivate virtual environment
deactivate  # On Linux/Mac
# Or simply close the terminal on Windows

# To reactivate
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Linux/Mac
```

### Failed Words

If some words fail during processing, the script will display them at the end:

```
❌ Failed Words (3):
==============================
 1. example_word_1
 2. example_word_2
 3. example_word_3
==============================
💡 You can manually retry these words later or check if they have typos.
```

## 📊 Performance

- **Processing Speed**: ~1 word per second (due to API rate limiting)
- **Success Rate**: ~98-99% (based on API availability)
- **Memory Usage**: Minimal (~50MB)
- **Total Processing Time**: ~18-20 minutes for 1,110 words

## 🔒 Security

- **Credentials**: Service account JSON file is excluded from version control
- **API Keys**: No API keys required for the free dictionary service
- **Permissions**: Service account has minimal required permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Free Dictionary API](https://dictionaryapi.dev/) for providing free vocabulary data
- [gspread](https://github.com/burnash/gspread) for Google Sheets integration
- Greg Mat for the comprehensive GRE vocabulary list

## 📧 Contact

If you have any questions or suggestions, please open an issue or contact the repository owner.

---

**Note**: This tool is designed for educational purposes to help with GRE vocabulary preparation. Please respect API rate limits and terms of service.