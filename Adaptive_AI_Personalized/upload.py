import urllib.request
import json
import os
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

zip_path = r'C:\Users\dell\OneDrive\Desktop\Adaptive_AI_Personalized_Learning_System.zip'
if not os.path.exists(zip_path):
    zip_path = 'Adaptive_AI_Personalized_Learning_System.zip'

with open(zip_path, 'rb') as f:
    file_bytes = f.read()

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body_catbox = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="reqtype"\r\n\r\nfileupload\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="time"\r\n\r\n72h\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="fileToUpload"; filename="Adaptive_AI_Personalized_Learning_System.zip"\r\n'
    f'Content-Type: application/zip\r\n\r\n'
).encode('utf-8') + file_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

try:
    req = urllib.request.Request(
        'https://litterbox.catbox.moe/resources/internals/api.php',
        data=body_catbox,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}', 'User-Agent': 'Mozilla/5.0'}
    )
    resp = urllib.request.urlopen(req, context=ssl_ctx)
    print("CATBOX_URL:", resp.read().decode('utf-8').strip())
except urllib.error.HTTPError as e:
    if e.code == 307:
        new_url = e.headers.get('Location')
        print("REDIRECT_URL:", new_url)
        req2 = urllib.request.Request(
            new_url,
            data=body_catbox,
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}', 'User-Agent': 'Mozilla/5.0'}
        )
        resp2 = urllib.request.urlopen(req2, context=ssl_ctx)
        print("CATBOX_SUCCESS_LINK:", resp2.read().decode('utf-8').strip())
    else:
        print("Catbox error:", e)
