import requests
from bs4 import BeautifulSoup
import json

# Constants
COUNTRY_CODE = "TJ"
COUNTRY_NAME = "Tajikistan"
COUNTRY_URL = f"https://bgp.he.net/country/{COUNTRY_CODE}"
WHOIS_URL = "https://bgp.he.net/super-lg/report/api/v1/whois/prefixes"
IRR_URL = "https://bgp.he.net/super-lg/report/api/v1/irr/prefixes"

# Flags
CHECK_WHOIS_PREFIXES = False  # Set to False to skip WHOIS validation

def handle_non_success_response(response, url):
    """Handles non-successful HTTP responses."""
    print(f"Error: Received status code {response.status_code} for URL: {url}")
    if response.status_code == 503:
        soup = BeautifulSoup(response.text, 'html.parser')
        h2_tag = soup.find('h2')
        if h2_tag:
            print(f"Details: {h2_tag.text.strip()}")
        else:
            print("Details: Unable to parse error details from the response body.")
    else:
        print(f"Message: {response.reason}")
    print("Aborting job due to non-complete received data.")
    exit(1)


def fetch_asn_data():
    response = requests.get(COUNTRY_URL)
    if response.status_code != 200:
        handle_non_success_response(response, COUNTRY_URL)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'asns'})

    if not table:
        print("ASN table not found on the page.")
        print("Aborting job due to non-complete received data.")
        exit(1)

    asn_data = []

    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        if len(columns) < 2:
            continue

        asn = columns[0].text.strip()
        name = columns[1].text.strip()

        # Fetch prefixes for the ASN
        prefix_url = f"https://bgp.he.net/super-lg/report/api/v1/prefixes/originated/{asn.lstrip('AS')}"
        prefix_response = requests.get(prefix_url)

        if prefix_response.status_code != 200:
            handle_non_success_response(prefix_response, prefix_url)

        prefixes = [
            p["Prefix"]
            for p in prefix_response.json().get("prefixes", [])
        ]

        validated_prefixes = validate_prefixes(prefixes)
        asn_data.append({
            'ASN': asn,
            'Name': name,
            'Prefixes': validated_prefixes
        })

        print(f"Finished processing ASN: {asn}")
        # Uncomment to process only the first ASN
        # break  

    return asn_data


def validate_prefixes(prefixes):
    """Validates prefixes in bulk using WHOIS and IRR APIs."""
    if not prefixes:
        return []

    validated_prefixes = []

    if CHECK_WHOIS_PREFIXES:
        # WHOIS validation
        whois_payload = {"prefixes": prefixes}
        whois_response = requests.post(WHOIS_URL, json=whois_payload)

        if whois_response.status_code != 200:
            handle_non_success_response(whois_response, WHOIS_URL)

        whois_data = whois_response.json()
        whois_valid_prefixes = {
            entry["Prefix"] for entry in whois_data.get("response", [])
            if entry.get("countrydata", {}).get("Iso3166_Name") == COUNTRY_NAME
        }
    else:
        whois_valid_prefixes = set(prefixes)

    # IRR validation
    irr_payload = {"prefixes": list(whois_valid_prefixes)}
    irr_response = requests.post(IRR_URL, json=irr_payload)

    if irr_response.status_code != 200:
        handle_non_success_response(irr_response, IRR_URL)

    irr_data = irr_response.json()
    for prefix in irr_data.get("response", []):
        if prefix.get("RouteValid") == "valid" or prefix.get("ParentValid") == "valid":
            validated_prefixes.append(prefix["Prefix"])

    return validated_prefixes


def main():
    asn_data = fetch_asn_data()
    if not asn_data:
        print("No ASN data available. Aborting job.")
        return

    # Output the results
    for entry in asn_data:
        print(f"ASN: {entry['ASN']}")
        print(f"Name: {entry['Name']}")
        print("Validated Prefixes:")
        for prefix in entry['Prefixes']:
            print(f"  - {prefix}")
        print("-" * 80)


if __name__ == "__main__":
    main()