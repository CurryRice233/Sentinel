import requests

# please set token and user id first
token = 'XXX'
my_id = "XXX"


def send_message(message, chat_id=my_id):
    url = "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + chat_id + "&text=" + message
    response = requests.get(url)
    if not response.ok:
        return False
    else:
        return True
