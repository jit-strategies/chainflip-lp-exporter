#!/usr/bin/env python3
import json
import requests
import logging

from prometheus_client import start_http_server, Metric, REGISTRY
from threading import Lock

lock = Lock

log = logging.getLogger('chainflip-lp-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class LPCollector:
    # cache decorator?
    def collect(self):
        with lock: 
            
            # Collection logic with cache ttl
            pass
    
    
if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9100, help='Port to listen on', default=9100)
    parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='Address to bind to', default='0.0.0.0')
    parser.add_argument('--config', nargs='?', const='config.yaml', help='Config file to use', default='config.yaml')
    args = parser.parse_args()
    log.info('exporter listening on http://%s:%d/metrics' % (args.addr, args.port))

    REGISTRY.register(LPCollector())
    start_http_server(int(args.port), addr=args.addr)

    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    log.error("Keyboard Interrupted")
    exit(0)
