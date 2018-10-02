# FIERCECROISSANT

FierceCroissant is a Pastebin scraper written in python designed to look for obfuscated pastes and save them. Once saved, decoders can then be applied to the pastes to de-obfuscate them for code samples.

## Getting Started

To scrape Pastebin, you must register your IP address in an account through Pastebin. For more details, please see https://pastebin.com/scraping

## Requirements

FierceCroissant uses Python 3. In addition, paste metadata is saved in a Mongo DB database (fc.pastemetadata by default). Last, the default messaging service to inform users is Hipchat.

## Methodology

FierceCroissant looks through the text of the 50 most recent pastes uploaded to pastebin. If the text size is over 40K and contains a string of 200 characters or more, it and its metadata will be saved. The text is then evaluated on its characteristics, and saved in a folder based on those characteristics performed by a regex search:

Pastes that begin with "TVoA", "TVpB", "TVpQ", "TVqA", "TVqQ", or "TVro" may be base64 snippets that decode to strings that begin with MZ (0x4d5a), and are thus MZ Executatble files. They are saved in the /base64pastes/ folder. (re.search(r'\A(TV(oA|pB|pQ|qQ|qA|ro|pA|ro))')) FierceCroissant will also save reversed base64 in the same path.

Strings that are made up of only 0 or 1 are saved in the /binarypastes/ folder.

Pastes with some combination of 200 characters in the hexadecimal system are saved in the /hexpastes/ folder (re.search(r'[2-9A-F]{200,}'))

Pastes that begin with "<?php" are saved in the /phppastes/ folder. (re.search(r'\A(<\?php)'))

Pastes that begin with "data:image" are saved in the /imgpastes/ folder. (re.search(r'\A(data:image)'))

Pastes that begin with "77 90 144 0 3 0 0 0" are saved in the /asciipastes/ folder (re.search(r'\A(77 90 144 0 3 0 0 0)')) as they decode into MZ Executables.

Pastes that do not match any of these will be saved in the root /pastes/ folder.

The decoder scripts (base64, binary, ASCII, and hex) will go through all the saved pastes in the respective folders and attempt to decode them. Any decoded pastes will be removed from that folder and put in its decoded form with the same name in the /decodedexes/ folder. 

Once decoded, it is expected that these pastes will be run by a sandbox environment such as Threatgrid or Joe's Sandbox to analyse their content and retrieve domain and URL information from the malicious samples. Alternatively, the hashsums of decoded executables could also be calculated to determine maliciousness.