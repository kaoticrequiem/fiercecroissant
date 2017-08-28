#!/usr/bin/python3
import requests, json, time, sys, os, re, configparser, base64
from bs4 import BeautifulSoup
from pymongo import MongoClient

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
# Config
config = configparser.ConfigParser()
config.read('config.ini')
if not config.has_section('main'):
    print("\nPlease ensure that your 'config.ini' exists and sets the appropriate values.\n")
    exit(1)
hip_token = config.get('main','hip_token')
pb_devkey = config.get('main', 'pb_devkey')
hip_room = config.get('main', 'hip_room')

def trendscraper():
    url = 'http://pastebin.com/api/api_post.php'
    payload = {'api_option': 'trends', 'api_dev_key': pb_devkey}
    r = requests.post(url, payload)
    pastetrend = r.text
    soup = BeautifulSoup(pastetrend, "lxml")
    raw_url = (soup.findAll("paste_url"))
    raw_text_url = 'http://pastebin.com/raw/'
    for line in raw_url:
        line = str(line)
        line = re.sub('</?paste_url>', '', line)
        paste_key = re.sub('http://pastebin.com/', '', line)
        paste_data = requests.get(raw_text_url + paste_key).text
        base64match = re.search(r'\w{200,}', paste_data)
        stringmatch = re.search(r'(A){20}', paste_data)
        if (base64match or stringmatch):
            headers = {'Content-Type': 'application/json'}
            card = {
                "style": "link",
                "url": line,
                "id": "fee4d9a3-685d-4cbd-abaa-c8850d9b1960",
                "title": "Pastebin Hit",
                "description": {
                    "format": "html",
                    "value": "<b>New Paste Seen: </b>" + line,
                },
                 "icon": {
                      "url": "https://pastebin.com/favicon.ico"
                },
                "date": 1443057955792
            }
            data_json = {'message': '<b>Joshtest - trendscraper part: New Paste<b>', 'card': card, 'message_format': 'html'}
            params = {'auth_token': hip_token}
            r = requests.post('https://api.hipchat.com/v2/room/' + hip_room + '/notification', data=json.dumps(data_json), headers=headers, params=params)

def scrapebin():
    result_limit = 50
    sleep_time = 30  # interval in seconds to sleep after each recent pastes batch
    minimum_length = 10  # ignore pastes shorter than this
    
    def http_get(url, params=None, tries=0):
        if params is None:
            params = {}
        if tries > 10:
            sys.exit('Exceeded 10 fetch retries. Are you banned?')
        res = requests.get(url, params, timeout=(4, 5))
        if res.status_code == requests.codes.ok:
            return res
        time.sleep(1)
        return http_get(url, params, tries + 1)
    
    def save_paste(path, data, separator=None):
        #if separator is None:
        #    separator = '\n\n---------- PASTE START ----------\n\n'
        with open(path, 'w', encoding='utf-8') as file:
        #    file.write(json.dumps(paste, sort_keys=True, indent=3, separators=(',', ': ')) + separator)
            file.write(data)
        return file.closed

    def metadatasave(paste, encodingtype):
        pastemetadata_dict = {'date': [], 'key': [], 'size': [], 'expire': [], 'syntax': [], 'user':[], 'encodingtype':[]}
        print("The dictionary entry should be blank:") + pastemetadata_dict
        pastemetadata_dict['date'] = paste['date']
        pastemetadata_dict['key'] = paste['key']
        pastemetadata_dict['size'] = paste['size']
        pastemetadata_dict['expire'] = paste['expire']
        pastemetadata_dict['syntax'] = paste['syntax']
        pastemetadata_dict['user'] = paste['user']
        pastemetadata_dict['encodingtype'] = encodingtype
        print("The dictionary entry is now:") + pastemetadata_dict

    
    while True:
        clock = int(time.strftime('%M', time.localtime()))
        if clock == 5:
            trendscraper()
        else:
            print("Waiting for new trends.")
        hits = 0
        recent_items = http_get('http://pastebin.com/api_scraping.php', params={'limit': result_limit}).json()
        for i, paste in enumerate(recent_items):
            paste_data = http_get(paste['scrape_url']).text
            paste_lang = paste['syntax']
            paste_size = paste['size']
            print('\rScraping: {0} / {1}'.format(i + 1, result_limit))
            filename = save_path + paste['key']
            #coll_pastemetadata.insert_one(paste)

            hexmatch = re.search(r'(\\x\w\w){100,}', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
            stringmatch = re.search(r'(A){20}', paste_data) #Searching for 10 'A's in a row.
            base64match = re.search(r'\w{200,}', paste_data) #Searching for 200 characters in a row to get non-words.
            base64sort = re.search(r'\A(TV(oA|pB|pQ|qQ|qA|ro|pA))', paste_data) #Searches the start of the paste for Base64 encoding structure.
            binarymatch = re.search(r'(0|1){200,}', paste_data) #Searches for 200 0's or 1's in a row.
            base64reversesort = re.search(r'\Z(AAAMAAQqVT)', paste_data) #Searches the end of the paste for reversed Base64 encoding structure.
            hexmatch2 = re.search(r'[2-9A-F]{200,}', paste_data) #Regex for Hexadecimal encoding.
            phpmatch = re.search(r'\A(<\?php)', paste_data) #Searches the start of a paste for php structure.
            imgmatch = re.search(r'\A(data:image)', paste_data) #Searches the start of a paste for data:image structure.
            if os.path.isfile(filename) or int(paste['size']) < minimum_length:
                continue
            
            #if (hexmatch or stringmatch or base64match or base64sort or binarymatch or base64reversesort or phpmatch or imgmatch) is None:
                #paste_data_dict['nomatch'].append(paste_data)                
                #paste_data_dict['pastekey'].append(pastekey)
                #coll_pasterawunsorted.insert_one(paste_data_dict)
            if ((base64match or stringmatch) and int(paste_size) > 40000) and paste_lang == "text":
                filename = save_path + paste['key']
                if (binarymatch and paste_data.isnumeric()):
                    filename = save_path_binary + paste['key']
                    encodingtype = 'binary'
                    save_paste(filename, paste_data)
                    metadata = metadatasave(paste, encodingtype)
                    try:
                        coll_pastemetadata.insert_one(metadata)
                    except:
                        continue
                elif (base64sort or base64reversesort):
                    filename = save_path_base64 + paste['key']
                    encodingtype = 'base64'
                    save_paste(filename, paste_data)
                    metadata = metadatasave(paste, encodingtype)
                    try:
                        coll_pastemetadata.insert_one(metadata)
                    except:
                        continue
                elif (hexmatch or hexmatch2):
                    filename = save_path_hex + paste['key']
                    encodingtype = 'hexadecimal'
                    save_paste(filename, paste_data)
                    metadata = metadatasave(paste, encodingtype)
                    try:
                        coll_pastemetadata.insert_one(metadata)
                    except:
                        continue
                elif phpmatch:
                    filename = save_path_php + paste['key']
                    encodingtype = 'php'
                    save_paste(filename, paste_data)
                    metadata = metadatasave(paste, encodingtype)
                    try:    
                        coll_pastemetadata.insert_one(metadata)
                    except:
                        continue
                elif imgmatch:
                    filename = save_path_img + paste['key']
                    encodingtype = 'img'
                    save_paste(filename, paste_data)
                    metadata = metadatasave(paste, encodingtype)
                    try:
                        coll_pastemetadata.insert_one(metadata)
                    except:
                        continue
                hits += 1
                headers = {'Content-Type': 'application/json'}
                card = {
                    "style": "link",
                    "url": "https://pastebin.com/" + paste['key'],
                    "id": "fee4d9a3-685d-4cbd-abaa-c8850d9b1960",
                    "title": "Pastebin Hit",
                    "description": {
                        "format": "html",
                        "value": "<b>TEST: New Paste Seen:</b> <a href='https://pastebin.com/'" + paste['key'] + " data-target='hip-connect-tester:hctester.dialog.simple' data-target-options='{\"options\":{\"title\":\"Custom Title\"}, \"parameters\":{\"from\":\"link\"}}'>https://pastebin.com/" + paste['key'] + "</a>"
                    },
                    "icon": {
                        "url": "https://pastebin.com/favicon.ico"
                    },
                    "date": 1443057955792
                }
                data_json = {'message': '<b>New Paste<b>', 'card': card, 'message_format': 'html'}
                params = {'auth_token': hip_token}
                r = requests.post('https://api.hipchat.com/v2/room/' + hip_room + '/notification', data=json.dumps(data_json),headers=headers, params=params)
            print("\nHits: {0}".format(hits))
        print("Waiting...\n\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    while True:
        scrapebin()
