#!/usr/bin/env python3
import json
import requests
import logging
import argparse
import yaml
import sys
import time
import datetime
from cachetools import cached, TTLCache
from decimal import Decimal
from itertools import chain

# from schema import Schema, And, Use, Optional, SchemaError
# confschema = Schema([ ... ]) # To validate config

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

UNIT_CONVERTER = {
    'USDC': Decimal(str(10 ** 6)),
    'ETH': Decimal(str(10 ** 18)),
    'BTC': Decimal(str(10 ** 8)),
    'DOT': Decimal(str(10 ** 10)),
    'FLIP': Decimal(str(10 ** 18))
}
cache = TTLCache(maxsize=10000, ttl=10)


def hex_amount_to_decimal(hex_string: str, asset: str) -> Decimal:
    """
    convert a hex string to a decimal number
    :param asset:
    :param hex_string:
    """
    return Decimal(str((int(hex_string, 16)) / UNIT_CONVERTER[asset]))


class LPCollector:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.header = {'Content-Type': 'application/json'}

    def collect(self):
        metric = Metric('chainflip_lp_metrics', 'Chainflip LP metrics', 'gauge')
        log.info('collecting metrics...')
        for addr in self.cfg['addresses']:
            data = self.get_balances(addr)
            all_balances = chain.from_iterable(
                data["result"]["balances"][blockchain].items() for
                blockchain in data["result"]["balances"]
            )
            for asset, hex_balance in all_balances:
                balance = hex_amount_to_decimal(hex_balance, asset)
                metric.add_sample('chainflip_lp_balance', value=float(balance), labels={'address': addr,
                                                                                        'asset_id': asset})
        yield metric

    @cached(cache)
    def get_balances(self, addr: str):
        data = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'cf_account_info',
            'params': [addr],
        }
        return requests.post(self.cfg['lp_host'], headers=self.header, data=json.dumps(data)).json()


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--config', nargs='?', const='config.yaml', help='Config file to use', default='config.yaml')
        args = parser.parse_args()
        with open(args.config) as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        log.info('exporter listening on http://%s:%d/metrics' % (cfg['listen_address'], cfg['listen_port']))
        REGISTRY.register(LPCollector(cfg))
        start_http_server(int(cfg['listen_port']), addr=cfg['listen_address'])

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log.warning("Keyboard Interrupted")
        exit(0)
