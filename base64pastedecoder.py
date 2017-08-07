import base64, os, requests

base64list = []
decoded_save_path = '/home/ubuntu/patrick/decodedexes/'

def writefile(filenm, stuff):
   writefile = open(filenm,'w')
   writefile.write(stuff)
   writefile.close()

for filename in os.listdir('/home/ubuntu/patrick/pastes/base64pastes/'): # absolute path of saved base64 sorted pastes
    sorted_path = os.path.join('/home/ubuntu/patrick/pastes/base64pastes/', filename)
    outputfile = decoded_save_path + filename
    with open(sorted_path, 'r') as f:
        paste_data = f.read()
        missing_padding = len(paste_data) % 4
        if missing_padding != 0:
            paste_data += b'='* (4 - missing_padding) # fix padding error
        decoded_paste = base64.b64decode(paste_data)
        writefile(outputfile, decoded_paste) # write pe32exe
        os.remove(sorted_path)
        f.close()