"""Localhost mock task panel. No hardware interfaces."""
import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from handoff import Runner, DemoAdapter

class Model:
    def __init__(self):
        self.lock = threading.Lock()
        self.runner = None
        self.active = False
        self.result = None

    def start(self, fail=False):
        with self.lock:
            if self.active:
                raise ValueError("A task is already running")
            self.runner = Runner(DemoAdapter("drive" if fail else None, 0.6))
            self.result = None
            self.active = True
            threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        result = self.runner.run()
        with self.lock:
            self.result = result
            self.active = False

    def stop(self):
        with self.lock:
            if self.active:
                self.runner.cancel.set()

    def reset(self):
        with self.lock:
            if self.active:
                raise ValueError("Stop and wait for completion before resetting")
            self.result = self.runner = None

    def status(self):
        with self.lock:
            return {"active": self.active, "mode": "simulation", "result": self.result,
                    "events": list(self.runner.events) if self.runner else []}

def server(port=8788):
    model = Model()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def send(self,code,body,kind="application/json"):
            data=body if isinstance(body,bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type",kind)
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=="/":self.send(200,(Path(__file__).parent/"panel.html").read_bytes(),"text/html; charset=utf-8")
            elif self.path=="/status":self.send(200,model.status())
            else:self.send(404,{"error":"Not found"})
        def do_POST(self):
            origin=self.headers.get("Origin")
            expected="http://127.0.0.1:"+str(self.server.server_port)
            if self.headers.get("Host")!=expected[7:] or (origin and origin!=expected):
                self.send(403,{"error":"Local origin required"});return
            try:
                length=int(self.headers.get("Content-Length","0"))
                if length<0 or length>1024 or self.headers.get("Content-Type")!="application/json":raise ValueError("Small JSON request required")
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):raise ValueError("JSON object required")
                if self.path=="/start":model.start(payload.get("fail") is True)
                elif self.path=="/stop":model.stop()
                elif self.path=="/reset":model.reset()
                else:self.send(404,{"error":"Not found"});return
                self.send(200,model.status())
            except (ValueError,TypeError) as e:self.send(400,{"error":str(e)})
    http=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    http.model=model
    return http

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--port",type=int,default=8788);a=p.parse_args()
    http=server(a.port);print(f"SIMULATION ONLY: http://127.0.0.1:{http.server_port}",flush=True)
    try:http.serve_forever()
    except KeyboardInterrupt:pass
    finally:http.model.stop();http.server_close()
