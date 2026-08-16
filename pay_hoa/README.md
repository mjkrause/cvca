# HOA Mailing Label Generator

A Python application for generating Avery mailing labels from HOA unit lists and member contact information.

## Overview

This tool merges HOA unit data with member contact information and generates properly formatted mailing labels for Avery label templates. It processes owner names, addresses, and automatically converts full state names to their standard two-letter abbreviations.

## Features

- Merges unit list data with member contact information
- Converts comma-separated owner names to ampersand format (e.g., "John Smith, Jane Smith" → "John Smith & Jane Smith")
- Automatically converts full state names to abbreviations (e.g., "California" → "CA")
- Generates CSV output formatted for Avery label printing
- Configurable file paths and output locations
- Comprehensive test coverage with mock data

## Requirements

- Python 3.8+
- pandas 2.3.3+

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pay-hoa
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application with default settings:

```bash
python app.py
```

By default, the application expects input files at:
- `~/Downloads/unit-list-download_2025-12-26.csv`
- `~/Downloads/member-contact-info_2025-12-26.csv`

And generates output at:
- `~/data/cvca/2025/avery_labels.csv`

### Custom Usage

You can customize the application by modifying the file paths in `app.py` or by using the `GenerateReport` class directly:

```python
from src.generate_report import GenerateReport

gr = GenerateReport(
    unit_list_csv_file='/path/to/unit-list.csv',
    member_contact_info_csv_file='/path/to/member-contact.csv',
    output_path='/path/to/output.csv'
)
gr.generate()
```

## Input File Format

### Unit List CSV
Expected columns:
- `Unit ID` - Unique identifier for each unit
- `Unit Title` - Unit number or designation
- `Unit Address` - Address in format: `street\ncity, state zipcode`

### Member Contact Info CSV
Expected columns:
- `Unit ID` - Unique identifier (must match Unit List)
- `Owner Names` - Owner name(s), comma-separated for multiple owners
- `Owner Address` - Mailing address in format: `street\ncity, state zipcode`

## Output Format

The generated CSV contains three columns formatted for Avery labels:
- `owner` - Owner name(s) with ampersands between multiple names
- `street_address` - Street address line
- `city_state_zip` - City, state abbreviation, and ZIP code

## Configuration

All hard-coded constants are centralized in `src/config.py`:

```python
from src.config import Config

# Column names
Config.COLUMN_OWNER_NAMES     # 'Owner Names'
Config.COLUMN_UNIT_ADDRESS    # 'Unit Address'
Config.COLUMN_OWNER_ADDRESS   # 'Owner Address'

# Separators
Config.SEPARATOR_COMMA        # ', '
Config.SEPARATOR_AMPERSAND    # ' & '

# Default paths
Config.get_default_output_path()
Config.get_default_unit_list_path()
Config.get_default_member_contact_info_path()
```

You can modify these constants to match your specific data format.

## Testing

The project includes comprehensive unit tests with mock data to ensure PII is not committed to the repository.

### Run Tests

```bash
python -m unittest test.test_generate_report -v
```

### Test Coverage

The test suite includes:
- CSV file merging functionality
- Owner name processing
- Address parsing and formatting
- State name abbreviation conversion
- Avery label generation
- Configuration validation
- Integration tests for full workflow

All tests use fake data located in `test/test_data/`:
- `fake_unit_list.csv`
- `fake_member_contact_info.csv`

## Project Structure

```
pay-hoa/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── src/
│   ├── __init__.py
│   ├── address.py                  # Address data classes
│   ├── config.py                   # Configuration constants
│   ├── generate_report.py          # Main report generation logic
│   └── state_name_map.py           # US state name to abbreviation mapping
└── test/
    ├── __init__.py
    ├── test_generate_report.py     # Unit tests
    └── test_data/
        ├── fake_unit_list.csv
        └── fake_member_contact_info.csv
```

## Development

### Adding New Features

1. Add configuration constants to `src/config.py`
2. Implement functionality in `src/generate_report.py`
3. Add corresponding tests in `test/test_generate_report.py`
4. Run tests to ensure nothing breaks

### Code Style

- Use type hints for function parameters and return values
- Follow PEP 8 style guidelines
- Add docstrings to public methods
- Keep functions focused and single-purpose

## Security Notes

- Never commit files containing real PII (personally identifiable information)
- Use the provided fake test data for testing
- Keep actual member data in your local Downloads folder (not tracked by git)
- The `.gitignore` file should exclude any files with real member data

## Troubleshooting

### "No such file or directory" Error
Ensure your input CSV files are in the expected locations or update the paths in `app.py`.

### "KeyError" on Column Name
Check that your input CSV files have the expected column names as defined in `src/config.py`.

### State Abbreviation Not Converting
Verify the state name matches exactly as listed in `src/state_name_map.py` (case-sensitive).

### Duplicate Unit IDs
The merge process uses left join and removes duplicates, keeping the first occurrence. Review your input data for duplicate Unit IDs.

## License

MIT Licencse

## Contributing

[Add contribution guidelines if applicable]

## Contact

Just use GitHub for communication.