"""Container frontend proxy to a native Apple Silicon Maya server."""
import http.client, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

upstream=urlsplit(os.environ.get('MAYA_UPSTREAM','http://host.docker.internal:8766'))
class Proxy(BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def forward(self):
  if self.path not in ('/','/api/options','/api/speech','/api/stream'):
   self.send_error(404); return
  conn=http.client.HTTPConnection(upstream.hostname,upstream.port or 80,timeout=600)
  try:
   body=self.rfile.read(int(self.headers.get('Content-Length',0))) if self.command=='POST' else None
   conn.request(self.command,self.path,body,{'Content-Type':'application/json'} if body else {})
   response=conn.getresponse(); self.send_response(response.status)
   self.send_header('Content-Type',response.getheader('Content-Type','application/octet-stream'))
   self.send_header('Cache-Control','no-store'); self.send_header('Transfer-Encoding','chunked'); self.end_headers()
   while True:
    chunk=response.read1(16384)
    if not chunk: break
    self.wfile.write(f'{len(chunk):X}\r\n'.encode()+chunk+b'\r\n'); self.wfile.flush()
   self.wfile.write(b'0\r\n\r\n'); self.wfile.flush()
  except (BrokenPipeError,ConnectionResetError): self.close_connection=True
  except Exception as e:
   print('Proxy error:',e,flush=True); self.close_connection=True
  finally: conn.close()
 do_GET=forward
 do_POST=forward
if __name__=='__main__':
 print('Maya proxy listening on 0.0.0.0:8765',flush=True)
 ThreadingHTTPServer(('0.0.0.0',8765),Proxy).serve_forever()
