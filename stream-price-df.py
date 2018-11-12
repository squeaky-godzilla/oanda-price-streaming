import argparse
import json
import pandas as pd
from oandapyV20 import API
from oandapyV20.exceptions import V20Error, StreamTerminated
from oandapyV20.endpoints.pricing import PricingStream
# from exampleauth import exampleAuth
from requests.exceptions import ConnectionError

def simplify_dict(d):
    rerun = True
    while rerun:
        rerun = False
        for k in list(d):
            v = d[k]
            if isinstance(v, list):
                rerun = True
                for idx, i in enumerate(v):
                    d["_".join([str(k),str(idx)])] = i
                del d[k]
            if isinstance(v, dict):
                rerun = True
                # simplify_dict(v)
                for key, value in v.items():
                    d["_".join([str(k),str(key)])] = value
                del d[k]
    return d


'''
time_point format:

{
  "type": "PRICE",
  "time": "2018-10-16T22:22:35.397047287Z",
  "bids": [
    {
      "price": "1.15732",
      "liquidity": 10000000
    }
  ],
  "asks": [
    {
      "price": "1.15751",
      "liquidity": 10000000
    }
  ],
  "closeoutBid": "1.15717",
  "closeoutAsk": "1.15766",
  "status": "tradeable",
  "tradeable": true,
  "instrument": "EUR_USD"
}
'''

# create the top-level parser
parser = argparse.ArgumentParser(prog='steaming_prices')
parser.add_argument('--timeout', default=0, type=float,
                    help='timeout in secs., default no timeout')
parser.add_argument('--count', default=0, type=int,
                    help='# of records to receive, default = unlimited.')
parser.add_argument('--instruments', type=str, nargs='?',
action='append', help='instruments')

args = parser.parse_args()

max_records = args.count

request_params = {}

if args.timeout:
    request_params = {"timeout": args.timeout}

with open('token') as token_file:
    auth_token_data = json.load(token_file)


api = API(access_token=auth_token_data['oanda-api-token'],
          environment="practice",
          request_params=request_params)

r = PricingStream(accountID=auth_token_data['oanda-account-id'], params={"instruments": ",".join(args.instruments)})

price_df = pd.DataFrame(columns=[])

n = 0
while True:
    try:
        for time_point in api.request(r):
            print(simplify_dict(time_point))
            n += 1
            if max_records and n >= max_records:
                r.terminate("maxrecs received: {}".format(max_records))

    except V20Error as e:
        # catch API related errors that may occur
        print("V20Error: {}\n".format(e))
        break
    except ConnectionError as e:
        print("Error: {}\n".format(e))
    except StreamTerminated as e:
        print("Stopping: {}\n".format(e))
        break
    except Exception as e:
        print("??? : {}\n".format(e))
        break