#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration file for HOA report generation."""

from pathlib import Path
from typing import List


class Config:
    """Configuration constants for HOA report generation."""

    # Column names
    COLUMN_OWNER_NAMES = 'Owner Names'
    COLUMN_UNIT_ADDRESS = 'Unit Address'
    COLUMN_OWNER_ADDRESS = 'Owner Address'
    COLUMN_UNIT_ID = 'Unit ID'
    COLUMN_UNIT_TITLE = 'Unit Title'
    COLUMN_UNIT_ADDRESS_X = 'Unit Address_x'
    COLUMN_UNIT_ADDRESS_Y = 'Unit Address_y'

    # Primary key for merging
    PRIMARY_KEY = 'Unit ID'

    # String separators
    SEPARATOR_COMMA = ', '
    SEPARATOR_AMPERSAND = ' & '
    SEPARATOR_NEWLINE = '\n'

    # Address parsing
    MAX_SPLIT_ADDRESS = 1

    # Output CSV field names
    OUTPUT_FIELD_NAMES: List[str] = ['owner', 'street_address', 'city_state_zip']

    # File paths (defaults - can be overridden)
    @staticmethod
    def get_default_output_path() -> str:
        """Get the default output path for Avery labels."""
        home = Path.home()
        return str(home / 'data' / 'cvca' / '2025' / 'avery_labels.csv')

    @staticmethod
    def get_default_unit_list_path() -> str:
        """Get the default path for unit list CSV file."""
        home = Path.home()
        return str(home / 'Downloads' / 'unit-list-download_2025-12-26.csv')

    @staticmethod
    def get_default_member_contact_info_path() -> str:
        """Get the default path for member contact info CSV file."""
        home = Path.home()
        return str(home / 'Downloads' / 'member-contact-info_2025-12-26.csv')

    # Temporary merged file
    TEMP_MERGED_FILE = 'merged.csv'
