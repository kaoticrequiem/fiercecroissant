import binascii, os, requests

base64list = []
save_path = '/home/ubuntu/patrick/decodedexes/'
length = 8

def writefile(path, binary):
    writefile = open(path,'wb')
    writefile.write(binary)
    writefile.close()

for filename in os.listdir('/home/ubuntu/patrick/pastes/binarypastes/'):
    sorted_path = os.path.join('/home/ubuntu/patrick/pastes/binarypastes/', filename)
    length = 8
    outputfile = save_path + filename
    with open(sorted_path, 'r') as f:
        paste_data = f.read()
        paste_data_length = [paste_data[i:i+length] for i in range(0,len(paste_data),length)]
        decoded_paste = ''.join([chr(int(c,base=2)) for c in paste_data_length])
        writefile(outputfile, decoded_paste)
        os.remove(sorted_path)
        f.close()

    
        