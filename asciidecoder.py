import base64, os

asciidirectory = os.getcwd() + '/pastes/asciipastes/' #relative path of ASCII pastes.
save_path = os.getcwd() + '/decodedexes/' #relative path of stored executables.

def writefile(filenm, stuff):
    writefile = open(filenm,'w')
    writefile.write(stuff)
    writefile.close()

for filename in os.listdir(asciidirectory): 
    paste = os.path.join(asciidirectory, filename)
    outputfile = save_path + filename
    with open(paste, 'r') as f:
        paste_data = f.read()
        try:
            paste_data_normalized = [int(i) for i in paste_data.split()]
            decoded_paste = "".join([chr(c) for c in paste_data_normalized])
            writefile(outputfile, decoded_paste) # write pe32exe
            os.remove(paste)
        except:
            continue
        f.close()