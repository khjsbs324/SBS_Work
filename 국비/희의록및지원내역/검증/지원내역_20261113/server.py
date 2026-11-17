from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import unquote,urlsplit
import json,mimetypes
root=Path(__file__).parent
runs=json.loads((root/'runs.json').read_text(encoding='utf-8'))
routes={}
for entry in runs:
    for g in 'ABC':
        folder=Path(entry['run'])/'03_지원자료'/(g+'그룹')
        content=json.loads((folder/'content.json').read_text(encoding='utf-8'))
        for name in content['files']+['학습자료.zip','guide.html','article.html']:
            routes['/'+entry['job']['lcode']+'/'+g+'/'+name]=folder/name
for name in ['jszip.min.js','docx-preview.min.js','preview.html']:
    routes['/qa/'+name]=root/name
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=routes.get(unquote(urlsplit(self.path).path))
        if not path or not path.is_file():self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream');self.end_headers();self.wfile.write(path.read_bytes())
    def log_message(self,*args):pass
print('Task-only preview on 127.0.0.1:8771',flush=True)
ThreadingHTTPServer(('127.0.0.1',8771),Handler).serve_forever()
