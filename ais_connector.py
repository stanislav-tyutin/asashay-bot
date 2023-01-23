import requests, json


class AisSession:

    def __init__(self, session):
        self.session = session

    def get_session(self):
        return self.session

    def set_session(self, value):
        self.session = value


def get_slots(ais_session: AisSession):
    url = 'https://ais.usvisa-info.com/en-am/niv/schedule/46265804/appointment/days/122.json?appointments[expedite]=false'
    cookies = dict(_yatri_session=ais_session.get_session())
    headers = _headers()
    response = requests.get(url, cookies=cookies, headers=headers)
    ais_session.set_session(response.cookies.get('_yatri_session'))
    return json.loads(response.text)


def _headers():
    headers = dict()
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,de;q=0.6'
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'ais.usvisa-info.com'
    headers['Referer'] = 'https://ais.usvisa-info.com/en-am/niv/schedule/46265804/appointment'
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    headers['X-Requested-With'] = 'XMLHttpRequest'
    headers['sec-ch-ua'] = 'Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = 'Linux'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-origin'
    return headers
