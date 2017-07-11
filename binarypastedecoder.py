import binascii, os, requests

base64list = []
save_path = os.getcwd() + '/decodedexes/'

def writefile(filenm, stuff):
   writefile = open(filenm,'w')
   writefile.write(stuff)
   writefile.close()

for filename in os.listdir("/home/ubuntu/patrick/pastes/binarypastes"):
   #request the raw text
   raw_text_url = 'http://pastebin.com/raw/'
   outputfile = save_path + filename + ' decoded.exe'
   paste_data = requests.get(raw_text_url + filename).text
   response = requests.get(raw_text_url + filename)
   if response.status_code == 404:
       continue
   #decode it
   os.rename("/home/ubuntu/patrick/pastes/binarypastes/" + filename, "/home/ubuntu/patrick/pastes/binarypastes/" + filename + " PROCESSED")
   try:
      decoded_paste = binascii.b2a_base64(paste_data)
      writefile(outputfile, decoded_paste)
   except:
      print("I failed trying to decode paste ") + filename
      raise
      continue
#throw that into TG
