import base64, os

base64directory = os.getcwd() + '/pastes/base64pastes/' #relative path of Base64 pastes.
save_path = os.getcwd() + '/decodedexes/' #relative path of stored executables.

def writefile(filenm, stuff):
    writefile = open(filenm,'w')
    writefile.write(stuff)
    writefile.close()

for filename in os.listdir(base64directory): 
    paste = os.path.join(base64directory, filename)
    outputfile = save_path + filename
    with open(paste, 'r') as f:
        paste_data = f.read()
        missing_padding = len(paste_data) % 4
        if missing_padding != 0:
            paste_data += b'='* (4 - missing_padding) # fix padding error
        try:
            decoded_paste = base64.b64decode(paste_data)
            writefile(outputfile, decoded_paste) # write pe32exe
            os.remove(paste)
        except:
            continue
        f.close()