#!/usr/bin/env python3
import json
import requests
import logging
import argparse
import yaml
import sys
import time

# from schema import Schema, And, Use, Optional, SchemaError

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

# confschema = Schema([ ... ]) # To validate config

class LPCollector:
    # cache decorator?
    def collect(self):
      metric = Metric('sample_metrics', 'sample metric values', 'gauge')
      # Collection logic with cache ttl
      metric.add_sample('foo', value=5.5, labels={'id': 'BTC'})
      yield metric
    
    
if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', nargs='?', const='config.yaml', help='Config file to use', default='config.yaml')
    args = parser.parse_args()
    with open(args.config) as f:
      cfg = yaml.load(f, Loader=yaml.FullLoader)
    
    log.info('exporter listening on http://%s:%d/metrics' % (cfg['listen_address'], cfg['listen_port']))

    REGISTRY.register(LPCollector())
    start_http_server(int(cfg['listen_port']), addr=cfg['listen_address'])

    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    log.error("Keyboard Interrupted")
    exit(0)
