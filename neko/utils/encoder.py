import base64
import urllib.parse

def base64_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()

def base64_decode(data):
    return base64.b64decode(data).decode()

def url_encode(data):
    return urllib.parse.quote(data)

def url_decode(data):
    return urllib.parse.unquote(data)

def xor_crypt(data, key):
    """
    Apply XOR encryption/decryption with a key.
    """
    if isinstance(data, str):
        data = data.encode()
    if isinstance(key, str):
        key = key.encode()
        
    output = bytearray()
    for i in range(len(data)):
        output.append(data[i] ^ key[i % len(key)])
    return output

def xor_crypt_string(data, key):
    res = xor_crypt(data, key)
    return res.decode(errors='ignore')
