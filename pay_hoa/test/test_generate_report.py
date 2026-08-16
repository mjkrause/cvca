#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open, MagicMock
import pandas as pd
from src.generate_report import GenerateReport
from src.address import Address, AddressAveryLabel
from src.config import Config


class TestGenerateReport(unittest.TestCase):

    def setUp(self) -> None:
        """Set up test fixtures using fake data files."""
        test_dir = os.path.dirname(os.path.abspath(__file__))
        self.unit_list_csv_file = os.path.join(test_dir, 'test_data', 'fake_unit_list.csv')
        self.member_contact_info_csv_file = os.path.join(test_dir, 'test_data', 'fake_member_contact_info.csv')

        self.assertTrue(os.path.exists(self.unit_list_csv_file), f"Test data file not found: {self.unit_list_csv_file}")
        self.assertTrue(os.path.exists(self.member_contact_info_csv_file), f"Test data file not found: {self.member_contact_info_csv_file}")

        # Create temporary output path for tests
        self.temp_output = tempfile.mktemp(suffix='.csv')

        self.gr = GenerateReport(
            unit_list_csv_file=self.unit_list_csv_file,
            member_contact_info_csv_file=self.member_contact_info_csv_file,
            output_path=self.temp_output
        )

    def tearDown(self) -> None:
        """Clean up temporary files."""
        if os.path.exists(self.temp_output):
            os.remove(self.temp_output)
        if os.path.exists(Config.TEMP_MERGED_FILE):
            os.remove(Config.TEMP_MERGED_FILE)

    def test_merge_with_real_files(self) -> None:
        """Test merging CSV files using real test data files."""
        df = self.gr.merge()

        # Check that merge was successful
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

        # Verify primary key column exists
        self.assertIn(Config.PRIMARY_KEY, df.columns)

        # Verify expected columns exist
        self.assertIn(Config.COLUMN_UNIT_ADDRESS, df.columns)
        self.assertIn(Config.COLUMN_OWNER_NAMES, df.columns)
        self.assertIn(Config.COLUMN_OWNER_ADDRESS, df.columns)

        # Verify no duplicate Unit IDs
        self.assertEqual(len(df[Config.PRIMARY_KEY]), len(df[Config.PRIMARY_KEY].unique()))

    def test_process_owner_name_with_comma(self) -> None:
        """Test that commas in owner names are replaced with ampersands."""
        input_name = "John Smith, Jane Smith"
        expected = "John Smith & Jane Smith"
        result = self.gr._process_owner_name(input_name)
        self.assertEqual(expected, result)

    def test_process_owner_name_without_comma(self) -> None:
        """Test that names without commas are unchanged."""
        input_name = "Bob Johnson"
        expected = "Bob Johnson"
        result = self.gr._process_owner_name(input_name)
        self.assertEqual(expected, result)

    def test_process_owner_names_list(self) -> None:
        """Test processing multiple owner names in a list of dictionaries."""
        data = [
            {Config.COLUMN_OWNER_NAMES: "Alice Williams, Charlie Williams"},
            {Config.COLUMN_OWNER_NAMES: "David Brown"},
            {Config.COLUMN_OWNER_NAMES: "Emma Davis, Frank Davis"}
        ]

        result = self.gr._process_owner_names(data)

        self.assertEqual(result[0][Config.COLUMN_OWNER_NAMES], "Alice Williams & Charlie Williams")
        self.assertEqual(result[1][Config.COLUMN_OWNER_NAMES], "David Brown")
        self.assertEqual(result[2][Config.COLUMN_OWNER_NAMES], "Emma Davis & Frank Davis")

    def test_parse_unit_address(self) -> None:
        """Test parsing unit address into Address components."""
        unit_address = "123 Oak Street\nSpringfield, Illinois 62701"

        result = self.gr.parse_unit_address(unit_address)

        self.assertIsInstance(result, Address)
        self.assertEqual(result.house_number, "123")
        self.assertEqual(result.street_name, "Oak Street")
        self.assertEqual(result.city_name, "Springfield")
        self.assertEqual(result.state_name, "Illinois")
        self.assertEqual(result.zip_code, "62701")

    def test_parse_unit_address_with_multi_word_street(self) -> None:
        """Test parsing address with multi-word street name."""
        unit_address = "456 Main Street East\nPortland, Oregon 97201"

        result = self.gr.parse_unit_address(unit_address)

        self.assertEqual(result.house_number, "456")
        self.assertEqual(result.street_name, "Main Street East")
        self.assertEqual(result.city_name, "Portland")
        self.assertEqual(result.state_name, "Oregon")
        self.assertEqual(result.zip_code, "97201")

    def test_replace_full_statename_with_abbreviation(self) -> None:
        """Test state name replacement with abbreviation."""
        test_cases = [
            ("Springfield, Illinois 62701", "Springfield, IL 62701"),
            ("Portland, Oregon 97201", "Portland, OR 97201"),
            ("Austin, Texas 78701", "Austin, TX 78701"),
            ("Denver, Colorado 80201", "Denver, CO 80201"),
        ]

        for input_address, expected in test_cases:
            result = self.gr.replace_full_statename_with_abbreviation(input_address)
            self.assertEqual(expected, result, f"Failed for input: {input_address}")

    def test_replace_full_statename_no_match(self) -> None:
        """Test that addresses without state names are unchanged."""
        input_address = "123 Main St, 12345"
        result = self.gr.replace_full_statename_with_abbreviation(input_address)
        self.assertEqual(input_address, result)

    def test_create_avery_labels(self) -> None:
        """Test creating Avery labels from data."""
        data = [
            {
                Config.COLUMN_OWNER_NAMES: "John Smith, Jane Smith",
                Config.COLUMN_OWNER_ADDRESS: "123 Oak Street\nSpringfield, Illinois 62701"
            },
            {
                Config.COLUMN_OWNER_NAMES: "Bob Johnson",
                Config.COLUMN_OWNER_ADDRESS: "456 Maple Avenue\nPortland, Oregon 97201"
            }
        ]

        result = self.gr.create_avery_labels(data)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], AddressAveryLabel)

        # Check first label
        self.assertEqual(result[0].owner, "John Smith & Jane Smith")
        self.assertEqual(result[0].street_address, "123 Oak Street")
        self.assertEqual(result[0].city_state_zip, "Springfield, IL 62701")

        # Check second label
        self.assertEqual(result[1].owner, "Bob Johnson")
        self.assertEqual(result[1].street_address, "456 Maple Avenue")
        self.assertEqual(result[1].city_state_zip, "Portland, OR 97201")

    @patch('src.generate_report.csv.DictWriter')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('pandas.read_csv')
    def test_generate_creates_output_file(self, mock_read_csv, mock_makedirs, mock_file, mock_writer) -> None:
        """Test that generate() creates output file with correct structure."""
        # Setup mock DataFrames
        mock_df1 = pd.DataFrame({
            Config.PRIMARY_KEY: ['001', '002'],
            Config.COLUMN_UNIT_ADDRESS: ['123 Oak St\nCity, State 12345', '456 Elm St\nTown, State 67890']
        })
        mock_df2 = pd.DataFrame({
            Config.PRIMARY_KEY: ['001', '002'],
            Config.COLUMN_OWNER_NAMES: ['John Smith, Jane Smith', 'Bob Johnson'],
            Config.COLUMN_OWNER_ADDRESS: ['123 Oak St\nCity, Illinois 12345', '456 Elm St\nTown, Oregon 67890']
        })
        mock_read_csv.side_effect = [mock_df1, mock_df2]

        # Setup mock writer
        mock_writer_instance = MagicMock()
        mock_writer.return_value = mock_writer_instance

        # Call generate
        self.gr.generate()

        # Verify output directory creation was attempted
        mock_makedirs.assert_called()

        # Verify file was opened for writing
        mock_file.assert_called_with(self.temp_output, 'w', newline='', encoding='utf-8')

        # Verify CSV writer was created with correct fieldnames
        mock_writer.assert_called_with(mock_file(), fieldnames=Config.OUTPUT_FIELD_NAMES)

        # Verify header was written
        mock_writer_instance.writeheader.assert_called_once()

        # Verify rows were written
        self.assertGreater(mock_writer_instance.writerow.call_count, 0)

    def test_config_constants_used(self) -> None:
        """Test that GenerateReport uses Config constants correctly."""
        self.assertEqual(self.gr.owner_names_key, Config.COLUMN_OWNER_NAMES)
        self.assertEqual(self.gr.unit_address, Config.COLUMN_UNIT_ADDRESS)
        self.assertEqual(self.gr.owner_address, Config.COLUMN_OWNER_ADDRESS)

    def test_merge_handles_left_join(self) -> None:
        """Test that merge uses left join to keep all units even without contact info."""
        df = self.gr.merge()

        # The unit list should have all entries preserved
        unit_df = pd.read_csv(self.unit_list_csv_file)
        self.assertEqual(len(df), len(unit_df))

    @patch('pandas.DataFrame.to_csv')
    def test_merge_saves_temp_file(self, mock_to_csv) -> None:
        """Test that merge saves temporary merged file."""
        self.gr.merge()

        # Check that to_csv was called with the temp file name
        calls = [call for call in mock_to_csv.call_args_list if Config.TEMP_MERGED_FILE in str(call)]
        self.assertGreater(len(calls), 0, "Temporary merged file was not saved")

    def test_output_path_default(self) -> None:
        """Test that default output path is used when not specified."""
        gr = GenerateReport(
            unit_list_csv_file=self.unit_list_csv_file,
            member_contact_info_csv_file=self.member_contact_info_csv_file
        )
        self.assertEqual(gr.output_path, Config.get_default_output_path())

    def test_output_path_custom(self) -> None:
        """Test that custom output path is used when specified."""
        custom_path = "/tmp/custom_output.csv"
        gr = GenerateReport(
            unit_list_csv_file=self.unit_list_csv_file,
            member_contact_info_csv_file=self.member_contact_info_csv_file,
            output_path=custom_path
        )
        self.assertEqual(gr.output_path, custom_path)

    def test_parse_unit_address_avery(self) -> None:
        """Test parsing unit address into AddressAveryLabel format."""
        unit_address = "123 Oak Street\nSpringfield, Illinois 62701"

        result = self.gr.parse_unit_address_avery(unit_address)

        self.assertIsInstance(result, AddressAveryLabel)
        self.assertEqual(result.street_address, "123 Oak Street")
        self.assertEqual(result.city_state_zip, "Springfield, Illinois 62701")
        self.assertIsNone(result.owner)

    def test_integration_full_workflow(self) -> None:
        """Integration test for the full workflow from merge to label creation."""
        # Merge the data
        df = self.gr.merge()
        self.assertGreater(len(df), 0)

        # Convert to dict and process owner names
        data = df.to_dict(orient='records')
        data = self.gr._process_owner_names(data)

        # Create Avery labels
        labels = self.gr.create_avery_labels(data)

        # Verify we got labels
        self.assertGreater(len(labels), 0)

        # Verify each label has required fields
        for label in labels:
            self.assertIsNotNone(label.owner)
            self.assertIsNotNone(label.street_address)
            self.assertIsNotNone(label.city_state_zip)

            # Verify ampersand replacement happened
            if ' & ' in label.owner or ', ' not in label.owner:
                # Either already has ampersand or didn't need replacement
                pass
            else:
                self.fail(f"Owner name '{label.owner}' should have commas replaced with ampersands")


class TestConfig(unittest.TestCase):
    """Tests for the Config class."""

    def test_column_constants(self) -> None:
        """Test that all column name constants are defined."""
        self.assertEqual(Config.COLUMN_OWNER_NAMES, 'Owner Names')
        self.assertEqual(Config.COLUMN_UNIT_ADDRESS, 'Unit Address')
        self.assertEqual(Config.COLUMN_OWNER_ADDRESS, 'Owner Address')
        self.assertEqual(Config.COLUMN_UNIT_ID, 'Unit ID')
        self.assertEqual(Config.PRIMARY_KEY, 'Unit ID')

    def test_separator_constants(self) -> None:
        """Test that separator constants are defined."""
        self.assertEqual(Config.SEPARATOR_COMMA, ', ')
        self.assertEqual(Config.SEPARATOR_AMPERSAND, ' & ')
        self.assertEqual(Config.SEPARATOR_NEWLINE, '\n')

    def test_output_field_names(self) -> None:
        """Test that output field names are correct."""
        expected = ['owner', 'street_address', 'city_state_zip']
        self.assertEqual(Config.OUTPUT_FIELD_NAMES, expected)

    def test_default_paths_return_strings(self) -> None:
        """Test that default path methods return valid strings."""
        self.assertIsInstance(Config.get_default_output_path(), str)
        self.assertIsInstance(Config.get_default_unit_list_path(), str)
        self.assertIsInstance(Config.get_default_member_contact_info_path(), str)


if __name__ == '__main__':
    unittest.main()
