import requests, json, time, sys, os, re, configparser
from bs4 import BeautifulSoup

keywords = [line.rstrip('\n') for line in open(os.getcwd() + '/keywords.txt', 'r').readlines()] #Keywords stored in a file to be searched for.
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

        for i, paste in enumerate(recent_items):
            paste_data = http_get(paste['scrape_url']).text
            paste_lang = paste['syntax']
            paste_size = paste['size']
            print('\rScraping: {0} / {1}'.format(i + 1, result_limit))
            filename = save_path + paste['key']
            stringmatch = re.search(r'(A){20}', paste_data) #Regex for 2x`0 'A's in a row.
            base64match = re.search(r'\w{200,}', paste_data) #Regex for 200 characters in a row.
            hexmatch = re.search(r'(\\x\w\w){100,}', paste_data) #Regex for hex formatted as "\\xDC", "\\x02", "\\xC4"
            binarymatch = re.search(r'(0|1){200,}', paste_data) #Regex for binary.
            base64sort = re.search(r'\A(TVqQAAMAAA)', paste_data) #Sorting for base64.
            base64reversesort = re.search(r'\Z(AAAMAAQqVT)', paste_data) #Sorting for reversed base64
            phpmatch = re.search(r'\A(<php\?)', paste_data)
            imgmatch = re.search(r'\A{data:image', paste_data)
            
            if os.path.isfile(filename) or int(paste['size']) < minimum_length:
                continue

            if ((base64match or stringmatch) and int(paste_size) > 40000) and paste_lang == "text":
                filename = save_path + paste['key']
                if binarymatch and paste_data.isnumeric():
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

if __name__ == "__main__":
    while True:
        scrapebin()
