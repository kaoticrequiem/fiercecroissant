#!/usr/bin/python3
import requests, json, time, sys, os, re, configparser, base64
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = MongoClient('localhost:27017')
db = client.fc

coll_pastemetadata = client.fc.pastemetadata
paste_data = ""
save_path = os.getcwd() + '/pastes/'  #Where keyword matching pastes get saved
save_path_base64 = save_path + '/base64pastes/'
save_path_hex = save_path + '/hexpastes/'
save_path_binary = save_path + '/binarypastes/'
save_path_php = save_path + '/phppastes/'
save_path_img = save_path + '/imgpastes/'
save_path_ascii = save_path + '/asciipastes/'
save_path_ps = save_path + '/pspastes/'

# Config file for token or key interactions.
config = configparser.ConfigParser()
config.read('config.ini')
if not config.has_section('main'):
    print("\nPlease ensure that your 'config.ini' exists and sets the appropriate values.\n")
    exit(1)
webex_token = config.get('main', 'webex_token')
webex_room = config.get('main', 'webex_room')


def scrapebin():
    
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

    def generate_message(paste_url, encodingtype):
        return("New paste seen:" + paste_url + " Encoded as:" + encodingtype)


    def webexpost():
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(webex_token)
        }
        message_content = {
        'roomId': webex_room,
        'markdown': generate_message(paste_url, encodingtype)
        }
        try:
            r = requests.post('https://api.ciscospark.com/v1/messages', data=json.dumps(message_content),headers=headers)
        except requests.exceptions.RequestException as e:
            print(('Exception raised trying to post to webex: {}').format(e))
            pass
    
    def base64reverser(s):
        return s[::-1]

    def fc_process(filename, encodingtype):
        save_paste(filename, paste_data)
        metadata = save_metadata(paste, encodingtype)
        coll_pastemetadata.insert_one(metadata)
        webexpost()

    while True:
        r = requests_retry_session().get('https://scrape.pastebin.com/api_scraping.php', params={'limit': 100})
        recent_items = None
        try:
            recent_items = r.json()
        except json.decoder.JSONDecodeError as e:
            print(('Exception raised decoding JSON: {}').format(e))
            continue
        for i, paste in enumerate(recent_items):
            pb_scrape_url = 'https://scrape.pastebin.com/api_scrape_item.php?i=' + paste['key']
            paste_data = requests.get(pb_scrape_url).text
            paste_lang = paste['syntax']
            paste_size = paste['size']
            paste_url = paste['full_url']
            stringmatch = re.search(r'(A){20}', paste_data) #Searching for 20 'A's in a row.
            stringmatch_76 = re.search(r'(A){76}', paste_data) #Searching for 76 'A's in a row.
            nonwordmatch = re.search(r'\w{200,}', paste_data) #Searching for 200 characters in a row to get non-words.
            base64match = re.search(r'\A(TV(oA|pB|pQ|qQ|qA|ro|pA))', paste_data) #Searches the start of the paste for Base64 encoding structure for an MZ executable.
            base64reversematch = re.search(r'((Ao|Bp|Qp|Qq|Aq|or|Ap)VT)\Z', paste_data) #Searches the end of the paste for reversed Base64 encoding structure for an MZ executable.
            binarymatch = re.search(r'(0|1){200,}', paste_data) #Searches for 200 0's or 1's in a row.
            binarymatch2 = re.search(r'([0|1][0|1][0|1][0|1][0|1][0|1][0|1][0|1] )', paste_data) #Searches for 0's or 1's in a group of 8 with a space.
            hexmatch = re.search(r'(\\x\w\w){100,}', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
            hexmatch2 = re.search(r'[2-9A-F]{200,}', paste_data) #Regex for Hexadecimal encoding.
            hexmatch3 = re.search(r'([0-9A-F ][0-9A-F ][0-9A-F ][0-9A-F ][0-9A-F ]){150,}', paste_data) #Regex for hex formatted as "4D ", "5A ", "00 " in groups of at least 150.
            phpmatch = re.search(r'\A(<\?php)', paste_data) #Searches the start of a paste for php structure.
            imgmatch = re.search(r'\A(data:image)', paste_data) #Searches the start of a paste for data:image structure.
            asciimatch = re.search(r'\A(77 90 144 0 3 0 0 0)', paste_data) #Searches the start of a paste for '77 90 144 0 3 0 0 0' to filter ASCII.
            powershellmatch = re.search(r'powershell', paste_data) #Searches the paste for 'powershell'.
            if ((((nonwordmatch or stringmatch) or (stringmatch_76 and (base64match or base64reversematch)) or hexmatch3) and int(paste_size) > 40000) or (powershellmatch and int(paste_size) < 10000)) and paste_lang == "text" and coll_pastemetadata.find_one({'key':paste['key']}) is None:
                if imgmatch:
                    fc_process(save_path_img + paste['key'],'img')
                elif phpmatch:
                    fc_process(save_path_php + paste['key'],'php')                                   
                elif (binarymatch and paste_data.isnumeric()) or binarymatch2:
                    fc_process(save_path_binary + paste['key'],'binary')
                elif (base64reversematch):
                    filename = save_path_base64 + paste['key']
                    encodingtype = 'reverse_base64'
                    save_paste(filename, base64reverser(paste_data))
                    metadata = save_metadata(paste, encodingtype)
                    coll_pastemetadata.insert_one(metadata)
                    webexpost()
                elif (base64match):
                    fc_process(save_path_base64 + paste['key'],'base64')
                elif asciimatch:
                    fc_process(save_path_ascii + paste['key'],'ASCII')
                elif (hexmatch or hexmatch2 or hexmatch3):
                    fc_process(save_path_hex + paste['key'],'hexadecimal')
                elif powershellmatch and (int(paste_size) < 10000):
                    fc_process(save_path_ps + paste['key'],'powershell')
                else:
                    fc_process(save_path + paste['key'],'other')
        time.sleep(60)
if __name__ == "__main__":
    while True:
        scrapebin()