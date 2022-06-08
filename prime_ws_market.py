import json, hmac, hashlib, base64
import asyncio
import time
import websockets
import sys
import os
uri = "wss://ws-feed.prime.coinbase.com"
ch = 'l2_data'
product_id = 'ETH-USD'
PASSPHRASE = os.environ.get("PASSPHRASE")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SIGNING_KEY = os.environ.get("SIGNING_KEY")
SVC_ACCOUNTID = os.environ.get("SVC_ACCOUNTID")
s = time.gmtime(time.time())
TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", s)
async def main_loop():
    async with websockets.connect(uri, ping_interval=None, max_size=None) as websocket:
        signature = await sign(ch, ACCESS_KEY, SIGNING_KEY, SVC_ACCOUNTID, "", product_id)
        print(signature)
        auth_message = json.dumps({
            "type": "subscribe",
            "channel": ch,
            "access_key": ACCESS_KEY,
            "api_key_id": SVC_ACCOUNTID,
            "timestamp": TIMESTAMP,
            "passphrase": PASSPHRASE,
            "signature": signature,
            "portfolio_id": "",
            "product_ids": [product_id]
        })
        await websocket.send(auth_message)
        try:
            processor = None
            while True:
                response = await websocket.recv()
                parsed = json.loads(response)
                print(json.dumps(parsed, indent=3))
        except websockets.exceptions.ConnectionClosedError:
            print("Error caught")
            sys.exit(1)
async def sign(channel, key, secret, account_id, portfolio_id, product_ids):
    message = channel + key + account_id + TIMESTAMP + portfolio_id + product_ids
    print(message)
    signature = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature_b64 = base64.b64encode(signature).decode()
    print(signature_b64)
    return signature_b64
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())