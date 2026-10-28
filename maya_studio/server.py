import io, json, os, threading
from types import SimpleNamespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ.setdefault('HF_HOME', '/private/tmp/maya-huggingface')
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
ROOT = Path(__file__).parent
lock = threading.Lock()
model = None
languages = {'as':'Assamese','bn':'Bengali','en':'English','gu':'Gujarati','hi':'Hindi','kn':'Kannada','ml':'Malayalam','mr':'Marathi','or':'Odia','pa':'Punjabi','ta':'Tamil','te':'Telugu'}
voices = {
'Ahana':('Female','bn en gu hi kn ml mr or pa ta te'), 'Vaidehi':('Female','bn en gu hi kn ml mr or pa ta te'), 'Malini':('Female','bn en gu hi kn ml mr or pa ta te'), 'Charvi':('Female','bn en gu hi kn ml mr or pa ta te'), 'Jahnavi':('Female','bn en gu hi kn ml mr or ta te'), 'Anirban':('Male','bn en gu hi kn ml mr or pa ta te'), 'Nakul':('Male','bn en gu hi kn ml mr or pa ta te'), 'Vasant':('Male','bn en gu hi kn ml mr or ta te'), 'Siddhant':('Male','bn en gu hi kn ml mr or pa ta te'), 'Satvik':('Male','bn en gu hi kn ml mr or pa ta te'), 'Abhay':('Male','en hi'), 'Nivedita':('Female','en hi'), 'Ishwari':('Female','hi'), 'Ritvik':('Male','hi'), 'Vrinda':('Female','hi'), 'Sreekar':('Male','en hi te'), 'Kayal':('Female','en ta'), 'Shaunak':('Male','en hi'), 'Akshat':('Male','en hi'), 'Tanushree':('Female','en hi')}
class Handler(BaseHTTPRequestHandler):
 protocol_version = 'HTTP/1.1'
 def send(self, code, data, typ):
  self.send_response(code); self.send_header('Content-Type',typ); self.send_header('Content-Length',str(len(data))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(data)
 def do_GET(self):
  if self.path == '/': self.send(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
  elif self.path == '/api/options': self.send(200,json.dumps({'languages':languages,'voices':[{'name':n,'gender':v[0],'trained':v[1].split()} for n,v in voices.items()]}).encode(),'application/json')
  else: self.send(404,b'Not found','text/plain')
 def do_POST(self):
  global model
  if self.path not in ('/api/speech', '/api/stream'): return self.send(404,b'Not found','text/plain')
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0 < length <= 16384: raise ValueError('Invalid request size.')
   body=json.loads(self.rfile.read(length)); text=body.get('text','').strip(); lang=body.get('language'); voice=body.get('voice')
   if not text or len(text)>1000: raise ValueError('Enter between 1 and 1,000 characters.')
   if lang not in languages or voice not in voices: raise ValueError('Please select a valid language and voice.')
   with lock:
    if model is None:
     if os.environ.get('MAYA_BACKEND','mlx') == 'cuda':
      from maya3 import Maya3TTS
      model=Maya3TTS.from_pretrained('maya-research/maya2-native', max_seats=1)
     else:
      from mlx_audio.tts.utils import load
      model=load('maya-research/maya2-native')
    import soundfile as sf
    if self.path == '/api/stream':
     import numpy as np
     if os.environ.get('MAYA_BACKEND','mlx') == 'cuda':
      def cuda_stream():
       for pcm in model.stream(text, lang=lang, voice=voice, normalize=True):
        yield SimpleNamespace(audio=pcm.astype('float32') / 32768.0, sample_rate=24000)
      stream=cuda_stream()
     else:
      stream=model.generate(text, voice=voice, lang_code=lang, stream=True, streaming_interval=0.32)
     first=next(stream)
     if first.sample_rate != 24000: raise ValueError('Unexpected audio sample rate')
     self.send_response(200); self.send_header('Content-Type','application/octet-stream'); self.send_header('Transfer-Encoding','chunked'); self.send_header('Cache-Control','no-store'); self.end_headers()
     try:
      from itertools import chain
      for chunk in chain((first,),stream):
       samples=np.asarray(chunk.audio, dtype=np.float32).reshape(-1)
       pcm=(np.clip(samples,-1,1)*32767).astype('<i2').tobytes()
       if pcm: self.wfile.write(f'{len(pcm):X}\r\n'.encode()+pcm+b'\r\n'); self.wfile.flush()
      self.wfile.write(b'0\r\n\r\n'); self.wfile.flush()
     except Exception as e:
      print('Streaming interrupted:', str(e), flush=True); self.close_connection=True
     finally: stream.close()
     return
    if os.environ.get('MAYA_BACKEND','mlx') == 'cuda':
     result=SimpleNamespace(audio=model.generate(text, lang=lang, voice=voice, normalize=True), sample_rate=24000)
    else: result=next(model.generate(text, voice=voice, lang_code=lang))
    audio=io.BytesIO(); sf.write(audio, result.audio, result.sample_rate, format='WAV')
   self.send(200,audio.getvalue(),'audio/wav')
  except Exception as e:
   self.send(400,json.dumps({'error':str(e)}).encode(),'application/json')
if __name__ == '__main__':
 host=os.environ.get('MAYA_HOST','127.0.0.1'); port=int(os.environ.get('MAYA_PORT','8765'))
 print(f'Maya Voice Studio listening on {host}:{port}', flush=True)
 ThreadingHTTPServer((host,port),Handler).serve_forever()
