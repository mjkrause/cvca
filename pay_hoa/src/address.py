#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Address:
    owner1: str = None
    owner2: str = None
    house_number: str = None
    street_name: str = None
    city_name: str = None
    state_name: str = None
    zip_code: str = None

@dataclass
class AddressAveryLabel:
    owner: str = None
    street_address: str = None
    city_state_zip: str = None