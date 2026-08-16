#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.generate_report import GenerateReport
from src.config import Config

def main():
    unit_list_csv_file = Config.get_default_unit_list_path()
    member_contact_info_csv_file = Config.get_default_member_contact_info_path()

    gr = GenerateReport(
        unit_list_csv_file=unit_list_csv_file,
        member_contact_info_csv_file=member_contact_info_csv_file
    )
    gr.generate()


if __name__ == '__main__':
    main()
