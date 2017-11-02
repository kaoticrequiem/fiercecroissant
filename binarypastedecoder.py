import binascii, os

binarydirectory = os.getcwd() + '/pastes/binarypastes/' #relative path of binary pastes.
save_path = os.getcwd() + '/decodedexes/' #relative path of stored executables.

def writefile(filenm, stuff):
    writefile = open(filenm,'w')
    writefile.write(stuff)
    writefile.close()
    
for filename in os.listdir(binarydirectory):
    paste = os.path.join(binarydirectory, filename)
    length = 8
    outputfile = save_path + filename
    with open(paste, 'r') as f:
        paste_data = f.read()
        paste_data_length = [paste_data[i:i+length] for i in range(0,len(paste_data),length)]
        try:
            decoded_paste = ''.join([chr(int(c,base=2)) for c in paste_data_length])
            writefile(outputfile, decoded_paste)
            os.remove(paste)
        except:
            continue
        f.close()