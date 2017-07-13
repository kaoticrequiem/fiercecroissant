### This version of FierceCroissant utilizes multiprocessing in order to run the scraper and decoders at
### the same time to improve processing speed and ensure that we grab the raw paste as soon as it's found.
### In the event that Pastebin takes the paste offline, we won't miss the opportunity to grab the raw paste.

#!/usr/bin/python3

import requests, json, time, sys, os, re, configparser, base64
from bs4 import BeautifulSoup
from multiprocessing import Process

paste_data = ""
#hexmatch1 = re.search(r'\\x\w\w', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
#hexmatch2 = re.search(r'0[xX][0-9a-fA-F]+', paste_data) #Regex for hex formatted as "0x3E" or "0XC4"
#stringmatch = re.search(r'(A){10}', paste_data) #Regex for 10 'A's in a row.
#base64match = re.search(r'\w{30,}', paste_data) #Regex for Base64
#rmatch = re.search(r'(r)', paste_data)
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
        #paste_size = paste['size']
        base64match = re.search(r'\w{200,}', paste_data)
        stringmatch = re.search(r'(A){20}', paste_data)
        #print("The paste key is " + str(paste_key))
        #print("The first ten characters are " + str(is_there_something_here))
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
            r = requests.post('https://api.hipchat.com/v2/room/3370440/notification', data=json.dumps(data_json), headers=headers, params=params)

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
        if separator is None:
            separator = '\n\n---------- PASTE START ----------\n\n'

        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(paste, sort_keys=True, indent=3, separators=(',', ': ')) + separator)
            file.write(data)

        return file.closed

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

            hexmatch = re.search(r'(\\x\w\w){100,}', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
            stringmatch = re.search(r'(A){20}', paste_data) #Regex for 10 'A's in a row.
            base64match = re.search(r'\w{200,}', paste_data) #Regex for Base64
            base64sort = re.search(r'\A(TVqQAAMAAA)', paste_data) #Sorting for base64.
            binarymatch = re.search(r'(0|1){200,}', paste_data) #Regex for binary.
            base64reversesort = re.search(r'\Z(AAAMAAQqVT)', paste_data) #Sorting for reversed base64
            hexmatch = re.search(r'(0-9A-F){200,}', paste_data) #Regex for Hex.
            phpmatch = re.search(r'\A(<php\?)', paste_data)
            imgmatch = re.search(r'\A{data:image', paste_data)
            if os.path.isfile(filename) or int(paste['size']) < minimum_length:
                continue

            #print(paste_data)
            if ((base64match or stringmatch) and int(paste_size) > 40000) and paste_lang == "text":
                filename = save_path + paste['key']
                if (binarymatch and paste_data.isnumeric()):
                    filename = save_path_binary + paste['key']
                elif (base64sort or base64reversesort):
                    filename = save_path_base64 + paste['key']
                elif hexmatch:
                    filename = save_path_hex + paste['key']
                elif phpmatch:
                    filename = save_path_php + paste['key']
                elif imgmatch:
                    filename = save_path_img + paste['key']
                save_paste(filename, paste_data)
                hits += 1
                #print(filename)
                #print(paste_size)

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
                print (r)

        print("\nHits: {0}".format(hits))
        print("Waiting...\n\n")

        time.sleep(sleep_time)

def decodebase64():

    decoded_save_path = '/home/ubuntu/patrick/decodedexes/' # absolute path to save pe32exe

    def writefile(path, binary):
       writefile = open(path,'wb')
       writefile.write(binary)
       writefile.close()

    for filename in os.listdir('/home/ubuntu/patrick/pastes/base64pastes/'): # absolute path of saved base64 sorted pastes
        sorted_path = os.path.join('/home/ubuntu/patrick/pastes/base64pastes', filename)
        raw_text_url = 'http://pastebin.com/raw/'
        outputfile = decoded_save_path + filename
        paste_data = requests.get(raw_text_url + filename).text # get raw base64 text
        #print (paste_data)
        response = requests.get(raw_text_url + filename)
        if response.status_code == 404:
          continue
        missing_padding = len(paste_data) % 4
        if missing_padding != 0:
            paste_data += b'='* (4 - missing_padding) # fix padding error
        decoded_paste = base64.b64decode(paste_data)
        #print (decoded_paste)
        writefile(outputfile, decoded_paste) # write pe32exe
        os.remove(sorted_path)

if __name__ == "__main__":
    p1 = Process(target=scrapebin)
    p1.start()
    p2 = Process(target=decodebase64)
    p2.start()