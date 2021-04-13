#!/usr/bin/python3
# coding: utf-8

import argparse
import json
import sqlite3
import os
import re
import sys
import datetime
import requests  # pip3 install requests


def get_o365_json():

    try:
        base_site = "https://docs.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide"

        request = requests.get(base_site)
        site_source = request.text
        regex_pattern = r'"https://endpoints\.office\.com/endpoints/worldwide\?clientrequestid=[a-z0-9\-]+"'
        target_url = re.search(regex_pattern, site_source).group(0)[1:-1]

        request = requests.get(target_url)
        json_data = json.loads(request.text)

    except Exception as err:

        sys.exit(f"ERROR: {err}")

    return json_data


def remove_previous_entries():

    """
    This removes the old entries added by this script, to prevent duplicates
    """

    # Write to database with built-in delay if the database-file is busy
    data_written = False

    while not data_written:
        try:
            conn = sqlite3.connect(GRAVITY_DB_PATH)
            cur = conn.cursor()
            cur.execute(f"DELETE FROM domainlist where comment like '%{SCRIPT_IDENTITY}'")
            conn.commit()

            data_written = True

        except sqlite3.OperationalError as error:
            if str(error).startswith('Error: attempt to write a readonly database'):
                sys.exit("Script not running with enough permissions, exiting...")
            else:
                print(f"ERROR: {error}")
                sys.exit('Unknown error, exited!')

    return data_written


def whitelist_domain(domain):

    print(f"Will now attempt to whitelist {domain['domain']}")

    # TODO: Method to handle wildcard-domains, like *sample.example.
    # TODO: type: 2
    # TODO: domain: (\.|^)sample\.example\.com$

    # Write to database with built-in delay if the database-file is busy
    data_written = False

    while not data_written:
        try:
            conn = sqlite3.connect(GRAVITY_DB_PATH)
            cur = conn.cursor()

            columns = ', '.join(domain.keys())
            placeholders = ':' + ', :'.join(domain.keys())
            query = f"INSERT INTO domainlist ({columns}) VALUES ({placeholders})"

            cur.execute(query, domain)
            conn.commit()

            print("Domain successfully added to database\n-------------")
            data_written = True

        except sqlite3.OperationalError as error:
            if str(error).startswith('Error: attempt to write a readonly database'):
                sys.exit("Script not running with enough permissions, exiting...")
            else:
                pass
        except sqlite3.IntegrityError as error:
            if str(error).startswith('UNIQUE constraint failed'):
                print(f"Item {domain['domain']} already in database, ignoring")
                data_written = True
            else:
                print(f"ERROR: {error}")
                sys.exit('Unknown error, exited!')

        except Exception as error:
            print(f"ERROR: {error}")

    return data_written


all_domains = list()

SCRIPT_IDENTITY = "7zg2vf6k4"  # String to be able to fingerprint domains added by the script
PIHOLE_INSTALL_PATH = r'/etc/pihole'
GRAVITY_DB_PATH = os.path.join(PIHOLE_INSTALL_PATH, 'gravity.db')

# TODO: Script to remove all existing domains matching the fingerprint (to prevent duplicates)
remove_previous_entries()

o365_json = get_o365_json()

if o365_json:

    unique_urls = list()

    for item in o365_json:

        # TODO: Argparse flag to handle required or not
        if item.get('required') and item.get('urls'):
            for url in item.get('urls', ''):
                domain = dict()

                # Handles wildcard domains
                if '*.' in url:
                    url_parts = url.split('*.')
                    url = url_parts[-1].lstrip('.')

                domain['domain'] = url
                domain['comment'] = f"{item['serviceAreaDisplayName']} - {SCRIPT_IDENTITY}"

                if url not in unique_urls:
                    unique_urls.append(url)
                    all_domains.append(domain)

# Adds the items to the database
print(f"Will now add {len(all_domains)} domains to db...")

counter = 1
for domain in all_domains:
    print(f"{counter}/{len(all_domains)}")
    domain['type'] = 0
    domain['enabled'] = 1
    domain['date_added'] = int(datetime.datetime.timestamp(datetime.datetime.utcnow()))
    domain['date_modified'] = int(datetime.datetime.timestamp(datetime.datetime.utcnow()))

    whitelist_domain(domain)
    counter += 1

print("Finished!")
