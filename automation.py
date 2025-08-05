import gspread
import requests
import time
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIGURATION ==========
SERVICE_ACCOUNT_FILE = 'gre-vocab-api-fb00a8972dc3.json'
# Using Google Sheet IDs instead of names for more reliable access
SOURCE_SHEET_ID = '1jRATLVV34vATsL4Y67fZZXQc7qZPYc0c0Yk7Bykh4fw'  # Greg Mat Vocab List
TARGET_SHEET_ID = '15vHs62RjZ8ACfywWWQTr6JMKBe_vJ9JhdZGQVDgIhXE'  # GRE Vocabulary
TARGET_HEADERS = ['word', 'pos', 'meaning', 'example', 'similar word']

# ========== SETUP GOOGLE SHEETS ==========
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

# Open source and target sheets using spreadsheet IDs
try:
    # Source sheet (view-only)
    SOURCE_SHEET_ID = '1jRATLVV34vATsL4Y67fZZXQc7qZPYc0c0Yk7Bykh4fw'
    source_spreadsheet = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_spreadsheet.sheet1
    print("✅ Successfully opened source sheet")
    
    # Target sheet (editable)
    TARGET_SHEET_ID = '15vHs62RjZ8ACfywWWQTr6JMKBe_vJ9JhdZGQVDgIhXE'
    target_spreadsheet = client.open_by_key(TARGET_SHEET_ID)
    target_sheet = target_spreadsheet.sheet1
    print("✅ Successfully opened target sheet")
    
except Exception as e:
    print(f"❌ Error opening sheets: {e}")
    print("Make sure your service account has access to both sheets")
    exit(1)

# Set headers for target sheet (only if empty)
try:
    existing_headers = target_sheet.row_values(1)
    if not existing_headers or existing_headers[0] == '':
        target_sheet.clear()
        target_sheet.insert_row(TARGET_HEADERS, 1)
        print("✅ Headers added to target sheet")
    else:
        print("✅ Target sheet already has headers")
except Exception as e:
    print(f"⚠️  Warning: Could not set headers: {e}")

# ========== FETCH WORDS FROM SOURCE ==========
def extract_words_from_ranges():
    """Extract all non-empty words from specified ranges"""
    all_words = []
    
    # Define the ranges to search: (start_row, end_row, start_col, end_col)
    ranges_to_search = [
        (4, 33, 1, 19),   # A4:S33
        (37, 66, 1, 19),  # A37:S66  
        (70, 132, 1, 19)  # A70:S132
    ]
    
    print("🔍 Extracting words from specified ranges...")
    
    for range_idx, (start_row, end_row, start_col, end_col) in enumerate(ranges_to_search, 1):
        print(f"📍 Processing range {range_idx}: Row {start_row}-{end_row}, Col A-S")
        
        try:
            # Get all values in the range
            range_values = source_sheet.batch_get([f'A{start_row}:S{end_row}'])[0]
            
            # Extract words from each cell
            for row_idx, row in enumerate(range_values):
                for col_idx, cell_value in enumerate(row):
                    if cell_value and str(cell_value).strip():  # Check if cell is not empty
                        word = str(cell_value).strip()
                        # Only add words that start with lowercase letters and are alphabetic
                        if word and word[0].islower() and word.replace('-', '').replace("'", "").isalpha():
                            all_words.append(word.lower())
            
            print(f"✅ Range {range_idx} processed")
            
        except Exception as e:
            print(f"⚠️ Error processing range {range_idx}: {e}")
            continue
    
    # Remove duplicates while preserving order
    unique_words = []
    seen = set()
    for word in all_words:
        if word not in seen:
            unique_words.append(word)
            seen.add(word)
    
    return unique_words

try:
    filtered_words = extract_words_from_ranges()
    print(f"✅ Found {len(filtered_words)} unique words starting with lowercase letters")
    print(f"First 10 words: {filtered_words[:10]}")
    
    if len(filtered_words) == 0:
        print("❌ No words found. Exiting...")
        exit(1)
        
except Exception as e:
    print(f"❌ Error fetching words from source sheet: {e}")
    exit(1)

# ========== FUNCTION TO FETCH FROM DICTIONARY ==========
def get_word_details(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"⚠️  API returned status {response.status_code} for '{word}'")
            return None
            
        data = response.json()[0]
        
        # Extract details
        pos = data['meanings'][0].get('partOfSpeech', '')
        definitions = data['meanings'][0].get('definitions', [])
        meaning = definitions[0].get('definition', '') if definitions else ''
        example = definitions[0].get('example', '') if definitions and 'example' in definitions[0] else ''
        synonyms = ", ".join(definitions[0].get('synonyms', [])) if definitions and 'synonyms' in definitions[0] else ''

        return [word, pos, meaning, example, synonyms]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching word '{word}': {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"❌ Data parsing error for word '{word}': {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error fetching word '{word}': {e}")
        return None

# ========== PROCESS AND WRITE TO TARGET ==========
def get_existing_words_in_target():
    """Get list of words already in target sheet to avoid duplicates"""
    try:
        existing_words = target_sheet.col_values(1)[1:]  # Skip header
        return set(word.lower().strip() for word in existing_words if word)
    except Exception as e:
        print(f"⚠️ Could not fetch existing words: {e}")
        return set()

# Get existing words to avoid duplicates
existing_words = get_existing_words_in_target()
words_to_process = [word for word in filtered_words if word not in existing_words]

print(f"📋 Words already in target sheet: {len(existing_words)}")
print(f"🆕 New words to process: {len(words_to_process)}")

if len(words_to_process) == 0:
    print("✅ All words are already processed!")
    exit(0)

success_count = 0
error_count = 0
failed_words = []  # Track failed words

print(f"\n🚀 Starting to process {len(words_to_process)} new words...")
print("=" * 50)

for i, word in enumerate(words_to_process, 1):
    print(f"[{i}/{len(words_to_process)}] Fetching: {word}")
    
    word_data = get_word_details(word)
    if word_data:
        try:
            target_sheet.append_row(word_data)
            success_count += 1
            print(f"✅ Added '{word}' to sheet")
        except Exception as e:
            print(f"❌ Error writing '{word}' to sheet: {e}")
            failed_words.append(word)
            error_count += 1
    else:
        print(f"⚠️  Skipped '{word}' (not found or error)")
        failed_words.append(word)
        error_count += 1
    
    # Progress update every 10 words
    if i % 10 == 0:
        print(f"📊 Progress: {i}/{len(words_to_process)} processed, {success_count} successful, {error_count} errors")
    
    time.sleep(1)  # delay to avoid rate limit

print("=" * 50)
print(f"✅ Processing complete!")
print(f"📊 Final stats: {success_count} successful, {error_count} errors out of {len(words_to_process)} total words")
print(f"📈 Total words now in target sheet: {len(existing_words) + success_count}")

# Display failed words if any
if failed_words:
    print(f"\n❌ Failed Words ({len(failed_words)}):")
    print("=" * 30)
    for i, word in enumerate(failed_words, 1):
        print(f"{i:2d}. {word}")
    print("=" * 30)
    print("💡 You can manually retry these words later or check if they have typos.")
else:
    print("🎉 All words processed successfully!")

print("🔗 Check your target sheet:", "https://docs.google.com/spreadsheets/d/15vHs62RjZ8ACfywWWQTr6JMKBe_vJ9JhdZGQVDgIhXE/edit")
