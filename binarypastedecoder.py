import binascii, os, requests

base64list = []
save_path = '/home/ubuntu/patrick/decodedexes/'
length = 8

def writefile(filenm, stuff):
   writefile = open(filenm,'w')
   writefile.write(stuff)
   writefile.close()

for filename in os.listdir("/home/ubuntu/patrick/pastes/binarypastes"):
   #request the raw text
   raw_text_url = 'http://pastebin.com/raw/'
   outputfile = save_path + filename
   paste_data = requests.get(raw_text_url + filename).text
   response = requests.get(raw_text_url + filename)
   if response.status_code == 404:
       continue
   #decode it
   #os.rename("/home/ubuntu/patrick/pastes/binarypastes/" + filename, "/home/ubuntu/patrick/pastes/binarypastes/" + filename + " PROCESSED")
   if paste_data.isnumeric():
       try:
          paste_data_length = [paste_data[i:i+length] for i in range(0,len(paste_data),length)]
          decoded_paste = ''.join([chr(int(c,base=2)) for c in paste_data_length])
          writefile(outputfile, decoded_paste)
       except:
          print("I failed trying to decode paste ") + filename
          raise
          continue

    
        