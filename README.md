# asn_prefix_validator
A Python script to fetch and validate ASN-originated prefixes for the country code TJ (Tajikistan)


The script uses data from bgp.he.net and validates prefixes through WHOIS and IRR APIs, ensuring accurate country and route information. Includes debugging support, flexible configuration, and options for bulk validation.

The dependencies for your script have been saved in a requirements.txt file. 

The script requires the following dependencies:

```
pip install requests
pip install beautifulsoup4
```

Output example:

```
ASN: AS8847
Name: CJSC "Telecomm Technology"
Validated Prefixes:
  - 95.142.80.0/23
  - 95.142.90.0/24
  - 95.142.82.0/24
  - 95.142.93.0/24
  - 95.142.83.0/24
  - 95.142.94.0/23
  - 95.142.82.0/23
  - 95.142.84.0/23
  - 95.142.86.0/23
  - 95.142.80.0/24
  - 95.142.84.0/24
  - 95.142.92.0/24
  - 95.142.91.0/24
  - 95.142.89.0/24
  - 95.142.90.0/23
  - 95.142.86.0/24
  - 95.142.88.0/23
  - 95.142.80.0/20
  - 95.142.85.0/24
  - 185.166.56.0/22
  - 95.142.81.0/24
```
