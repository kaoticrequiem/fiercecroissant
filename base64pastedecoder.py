import base64, os, requests

base64list = []
save_path = os.getcwd() + '/decodedexes/'

def writefile(filenm, stuff):
   writefile = open(filenm,'w')
   writefile.write(stuff)
   writefile.close()

for filename in os.listdir("/home/ubuntu/patrick/pastes/base64pastes"):
   #request the raw text
   raw_text_url = 'http://pastebin.com/raw/'
   outputfile = save_path + filename + ' decoded.exe'
   paste_data = requests.get(raw_text_url + filename).text
   response = requests.get(raw_text_url + filename)
   if response.status_code == 404:
       continue
   #decode it
   os.rename("/home/ubuntu/patrick/pastes/base64pastes/" + filename, "/home/ubuntu/patrick/pastes/base64pastes/" + filename + " PROCESSED")
   missing_padding = len(paste_data) % 4
   if missing_padding != 0:
       paste_data += b'='* (4 - missing_padding)
   decoded_paste = base64.b64decode(paste_data)
# try:
  # 	decoded_paste = base64.b64decode(paste_data)
  # except Exception:
  # 	pass
   writefile(outputfile, decoded_paste)
   #throw that into TG
