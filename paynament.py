import requests
import logging

from config import QIWI_ACCOUNT, QIWI_TOKEN, oneday, threeday, sevenday

logging.basicConfig(
    level=logging.INFO,
    filename='logs.log',
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)


def cheak_payment(id):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
    parameters = {'rows': '50', 'operation': 'IN'}
    h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + QIWI_ACCOUNT + '/payments', params=parameters)
    req = h.json()

    for operation in req['data']:
        if operation['comment'] == id:
            if operation['sum']['amount'] == oneday:
                return 86400
            elif operation['sum']['amount'] == threeday:
                return 259200
            elif operation['sum']['amount'] == sevenday:
                return 604800
            else:
                return False
    return False
