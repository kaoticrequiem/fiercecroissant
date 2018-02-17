import os

hexdirectory = os.getcwd() + '/pastes/hexpastes/' #relative path of binary pastes.
save_path = os.getcwd() + '/decodedexes/' #relative path of stored executables.

def writefile(filenm, stuff):
    writefile = open(filenm,'w')
    writefile.write(stuff)
    writefile.close()
    
for filename in os.listdir(hexdirectory):
    paste = os.path.join(hexdirectory, filename)
    outputfile = save_path + filename
    with open(paste, 'r') as f:
        paste_data = f.read()
        try:
            decoded_paste = bytearray.fromhex(paste_data)
            writefile(outputfile, decoded_paste)
            os.remove(paste)
        except:
            continue
        f.close()
