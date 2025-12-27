#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
from typing import Dict, List
from src.address import Address, AddressAveryLabel
from src.state_name_map import state_name_map
from src.config import Config
import csv
import logging
from dataclasses import asdict
from pathlib import Path


logger = logging.getLogger(__file__)


class GenerateReport:

    def __init__(self, unit_list_csv_file: str, member_contact_info_csv_file: str, output_path: str = None):
        self.unit_list_csv_file: str = unit_list_csv_file
        self.member_contact_info_csv_file: str = member_contact_info_csv_file
        self.output_path: str = output_path or Config.get_default_output_path()
        self.owner_names_key: str = Config.COLUMN_OWNER_NAMES
        self.unit_address: str = Config.COLUMN_UNIT_ADDRESS
        self.owner_address: str = Config.COLUMN_OWNER_ADDRESS
        self.state_name_map: Dict[str, str] = state_name_map()

    def generate(self) -> None:
        df = self.merge()
        data: List[dict] = df.to_dict(orient='records')
        data = self._process_owner_names(data=data)

        address_avery_labels = self.create_avery_labels(data=data)

        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output_path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=Config.OUTPUT_FIELD_NAMES)
            writer.writeheader()
            for address_avery_label in address_avery_labels:
                writer.writerow(asdict(address_avery_label))

    def load(self) -> List[dict]:
        data: list = []
        with open(file=self.csv_file, mode='r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                data.append(row)

        return data

    def merge(self) -> pd.DataFrame:
        # Load the CSV files
        df1 = pd.read_csv(self.unit_list_csv_file)
        df2 = pd.read_csv(self.member_contact_info_csv_file)

        # Merge on the common column
        merged_df = pd.merge(df1, df2, on=Config.PRIMARY_KEY, how='left')

        # Save the result
        merged_df.to_csv(Config.TEMP_MERGED_FILE, index=False)

        # Drop duplicate Unit Address column from second dataframe if it exists
        if Config.COLUMN_UNIT_ADDRESS_Y in merged_df.columns:
            merged_df = merged_df.drop(columns=Config.COLUMN_UNIT_ADDRESS_Y)

        # Remove duplicates
        merged_df = merged_df.drop_duplicates(subset=[Config.PRIMARY_KEY], keep='first')

        # Rename Unit Address_x back to Unit Address if needed
        if Config.COLUMN_UNIT_ADDRESS_X in merged_df.columns:
            merged_df = merged_df.rename(columns={Config.COLUMN_UNIT_ADDRESS_X: Config.COLUMN_UNIT_ADDRESS})

        return merged_df


    def _process_owner_names(self, data: List[dict]) -> List[dict]:
        for item in data:
            item[self.owner_names_key] = self._process_owner_name(name_value=item[self.owner_names_key])

        return data

    def _process_owner_name(self, name_value: str) -> str:
        if Config.SEPARATOR_COMMA not in name_value:
            return name_value
        else:
            return name_value.replace(Config.SEPARATOR_COMMA, Config.SEPARATOR_AMPERSAND)

    def parse_unit_address(self, unit_address: str) -> Address:
        street_address, city_state_zip = unit_address.split(sep=Config.SEPARATOR_NEWLINE)
        house_number, street_name = street_address.split(sep=' ', maxsplit=Config.MAX_SPLIT_ADDRESS)
        city_name, state_zip = city_state_zip.split(',', 1)
        state_name, zip_code = state_zip.split()

        return Address(
            house_number=house_number,
            street_name=street_name,
            city_name=city_name,
            state_name=state_name,
            zip_code=zip_code,
        )

    def create_avery_labels(self, data: List[dict]) -> List[AddressAveryLabel]:
        avery_labels: list = []
        for item in data:
            logger.info(f'item = {item}')
            address = item[self.owner_address]
            logger.info(f'address = {address}')
            street_address, city_state_zip = address.split(sep=Config.SEPARATOR_NEWLINE)
            city_state_zip = self.replace_full_statename_with_abbreviation(city_state_zip)

            address_avery_label = AddressAveryLabel(
                owner=self._process_owner_name(name_value=item[self.owner_names_key]),
                street_address=street_address,
                city_state_zip=city_state_zip
            )

            avery_labels.append(address_avery_label)

        return avery_labels

    def parse_unit_address_avery(self, unit_address: str) -> AddressAveryLabel:
        street_address, city_state_zip = unit_address.split(sep=Config.SEPARATOR_NEWLINE)

        return AddressAveryLabel(
            owner=None,
            street_address=street_address,
            city_state_zip=city_state_zip,
        )

    def replace_full_statename_with_abbreviation(self, address: str) -> str:
        """Replace the state name with the abbreviation."""
        for state, abbrev in self.state_name_map.items():
            if state in address:
                address = address.replace(state, abbrev)
                break
        return address
