#!/usr/bin/python3
import requests, json, time, sys, os, re, configparser, base64
from bs4 import BeautifulSoup
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = MongoClient('localhost:27017')
db = client.fc
coll_pasterawunsorted = client.fc.pasterawunsorted
coll_pastemetadata = client.fc.pastemetadata

paste_data = ""
save_path = os.getcwd() + '/pastes/'  #Where keyword matching pastes get saved
save_path_base64 = save_path + '/base64pastes/'
save_path_hex = save_path + '/hexpastes/'
save_path_binary = save_path + '/binarypastes/'
save_path_php = save_path + '/phppastes/'
save_path_img = save_path + '/imgpastes/'
save_path_ascii = save_path + '/asciipastes/'

# Config
config = configparser.ConfigParser()
config.read('config.ini')
if not config.has_section('main'):
    print("\nPlease ensure that your 'config.ini' exists and sets the appropriate values.\n")
    exit(1)
hip_token = config.get('main','hip_token')
pb_devkey = config.get('main', 'pb_devkey')
hip_room = config.get('main', 'hip_room')


def scrapebin():
    result_limit = 50
    sleep_time = 30  # interval in seconds to sleep after each recent pastes batch
    
    def requests_retry_session(retries=10, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None, params=None):
        session = session or requests.Session()
        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)      
        session.mount('https://', adapter)
        return session
    
    def save_paste(path, data):
        with open(path, 'w', encoding='utf-8') as file:
            file.write(data)
        return file.closed

    def save_metadata(paste, encodingtype):
        pastemetadata_dict = {'date': [], 'key': [], 'size': [], 'expire': [], 'syntax': [], 'user':[], 'encodingtype':[]}
        pastemetadata_dict.update({'date':paste['date'], 'key':paste['key'], 'size':paste['size'], 'expire':paste['expire'], 'syntax':paste['syntax'], 'user':paste['user'], 'encodingtype':encodingtype})
        return pastemetadata_dict

    def hipchatpost():
        #Alerts a HipChat room about a new paste.
        headers = {'Content-Type': 'application/json'}
        card = {
            "style": "link",
            "url": paste_url,
            "id": "fee4d9a3-685d-4cbd-abaa-c8850d9b1960",
            "title": "Pastebin Hit",
            "description": {
                "format": "html",
                "value": "<b>New Paste Seen:</b>" + paste_url + " Encoded as:" + encodingtype
                    },
        "icon": {
            "url": "https://pastebin.com/favicon.ico"
                    },
        "date": 1443057955792
        }
        data_json = {'message': '<b>New Paste<b>', 'card': card, 'message_format': 'html'}
        params = {'auth_token': hip_token}
        try:
            r = requests.post('https://api.hipchat.com/v2/room/' + hip_room + '/notification', data=json.dumps(data_json),headers=headers, params=params)
        except:
            pass

    while True:
        hits = 0
        recent_items = requests_retry_session().get('https://pastebin.com/api_scraping.php', params={'limit': 50}).json()
        for i, paste in enumerate(recent_items):
            paste_data = requests.get(paste['scrape_url']).text
            paste_lang = paste['syntax']
            paste_size = paste['size']
            paste_url = paste['full_url']
            print('\rScraping: {0} / {1}'.format(i + 1, result_limit))
            stringmatch = re.search(r'(A){20}', paste_data) #Searching for 20 'A's in a row.
            stringmatch_76 = re.search(r'(A){76}', paste_data) #Searching for 76 'A's in a row.
            nonwordmatch = re.search(r'\w{200,}', paste_data) #Searching for 200 characters in a row to get non-words.
            base64sort = re.search(r'\A(TV(oA|pB|pQ|qQ|qA|ro|pA))', paste_data) #Searches the start of the paste for Base64 encoding structure for an MZ executable.
            base64reversesort = re.search(r'((Ao|Bp|Qp|Qq|Aq|or|Ap)VT)\Z', paste_data) #Searches the end of the paste for reversed Base64 encoding structure for an MZ executable.
            binarysort = re.search(r'(0|1){200,}', paste_data) #Searches for 200 0's or 1's in a row.
            hexmatch = re.search(r'(\\x\w\w){100,}', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
            hexmatch2 = re.search(r'[2-9A-F]{200,}', paste_data) #Regex for Hexadecimal encoding.
            hexmatch3 = re.search(r'([0-9A-F ][0-9A-F ][0-9A-F ][0-9A-F ][0-9A-F ]){150,}', paste_data) #Regex for hex formatted as "4D ", "5A ", "00 " in groups of at least 150.
            phpmatch = re.search(r'\A(<\?php)', paste_data) #Searches the start of a paste for php structure.
            imgmatch = re.search(r'\A(data:image)', paste_data) #Searches the start of a paste for data:image structure.
            asciimatch = re.search(r'\A(77 90 144 0 3 0 0 0)', paste_data) #Searches the start of a paste for '77 90 144 0 3 0 0 0' to filter ASCII.
            if (((nonwordmatch or stringmatch) or (stringmatch_76 and (base64sort or base64reversesort)) or hexmatch3) and int(paste_size) > 40000) and paste_lang == "text" and coll_pastemetadata.find_one({'key':paste['key']}) is None:
                if (binarysort and paste_data.isnumeric()):
                    filename = save_path_binary + paste['key']
                    encodingtype = 'binary'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                elif (base64sort or base64reversesort):
                    filename = save_path_base64 + paste['key']
                    encodingtype = 'base64'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype) 
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                elif (hexmatch3 and asciimatch) and paste_data.isnumeric():
                    filename = save_path_ascii + paste['key']
                    encodingtype = "ASCII"
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                elif (hexmatch or hexmatch2 or hexmatch3) not paste_data.isnumeric():
                    filename = save_path_hex + paste['key']
                    encodingtype = 'hexadecimal'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                elif phpmatch:
                    filename = save_path_php + paste['key']
                    encodingtype = 'php'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                elif imgmatch:
                    filename = save_path_img + paste['key']
                    encodingtype = 'img'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                else:
                    filename = save_path + paste['key']
                    encodingtype = 'other'
                    save_paste(filename, paste_data)
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    hipchatpost()
                hits += 1
            print("\nHits: {0}".format(hits))
        print("Waiting...\n\n")
        time.sleep(sleep_time)
if __name__ == "__main__":
    while True:
        scrapebin()
