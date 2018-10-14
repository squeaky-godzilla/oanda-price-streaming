import argparse
import json
from oandapyV20 import API
from oandapyV20.exceptions import V20Error, StreamTerminated
from oandapyV20.endpoints.pricing import PricingStream
# from exampleauth import exampleAuth
from requests.exceptions import ConnectionError

# create the top-level parser
parser = argparse.ArgumentParser(prog='steaming_prices')
parser.add_argument('--nice', action='store_true', help='json indented')
parser.add_argument('--timeout', default=0, type=float,
                    help='timeout in secs., default no timeout')
parser.add_argument('--count', default=0, type=int,
                    help='# of records to receive, default = unlimited.')
parser.add_argument('--instruments', type=str, nargs='?',
action='append', help='instruments')

args = parser.parse_args()

MAXREC = args.count

request_params = {}

if args.timeout:
    request_params = {"timeout": args.timeout}

with open('token') as token_file:
    auth_token_data = json.load(token_file)


api = API(access_token=auth_token_data['oanda-api-token'],
          environment="practice",
          request_params=request_params)

r = PricingStream(accountID=auth_token_data['oanda-account-id'], params={"instruments": ",".join(args.instruments)})

n = 0
while True:
    try:
        for R in api.request(r):
            if args.nice:
                R = json.dumps(R, indent=2)
            print(R)
            n += 1
            if MAXREC and n >= MAXREC:
                r.terminate("maxrecs received: {}".format(MAXREC))

    except V20Error as e:
        # catch API related errors that may occur
        with open("LOG", "a") as LOG:
            LOG.write("V20Error: {}\n".format(e))
        break
    except ConnectionError as e:
        with open("LOG", "a") as LOG:
            LOG.write("Error: {}\n".format(e))
    except StreamTerminated as e:
        with open("LOG", "a") as LOG:
            LOG.write("Stopping: {}\n".format(e))
        break
    except Exception as e:
        with open("LOG", "a") as LOG:
            LOG.write("??? : {}\n".format(e))
        break