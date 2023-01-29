import requests, json
from pyquery import PyQuery as pq
from time import sleep
import logging


class AisSession:

    def __init__(self, session):
        self.session = session
        self.etag = None

    def get_session(self):
        return self.session

    def set_session(self, value):
        self.session = value

    def get_etag(self):
        return self.etag

    def set_etag(self, value):
        self.etag = value


def get_slots(ais_session: AisSession):
    url = 'https://ais.usvisa-info.com/en-am/niv/schedule/46265804/appointment/days/122.json?appointments[expedite]=false'
    cookies = dict(_yatri_session=ais_session.get_session())
    response = requests.get(url, cookies=cookies, headers=_api_headers(ais_session.get_etag()))
    ais_session.set_session(response.cookies.get('_yatri_session'))
    ais_session.set_etag(response.headers.get('ETag'))
    logging.debug(f'GET SLOTS {response.status_code}')
    if response.status_code == 200:
        return True, json.loads(response.text)
    elif response.status_code == 304:
        return False, None
    else:
        logging.debug(response.status_code, response.text)
        raise RuntimeError('Unexpected response')


def create_session(login, password):
    form_url = 'https://ais.usvisa-info.com/en-am/niv/users/sign_in'
    form_response = requests.get(form_url, headers=_html_headers())
    ais_session = AisSession(form_response.cookies.get('_yatri_session'))
    parsed_page = pq(form_response.content)
    csrf_tag = parsed_page('meta[name="csrf-token"]')[0]
    csrf_value = csrf_tag.attrib['content']

    sleep(3)

    cookies = dict(_yatri_session=ais_session.get_session())
    data = dict(utf8='✓', policy_confirmed=1, commit='Sign In')
    data['user[email]'] = login
    data['user[password]'] = password
    sign_in_response = requests.post(form_url, headers=_form_headers(csrf_value), cookies=cookies, data=data)
    ais_session.set_session(sign_in_response.cookies.get('_yatri_session'))

    return ais_session


def _api_headers(etag):
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
    if etag is not None:
        headers['If-None-Match'] = etag
        logging.debug(f'ETAG used {etag}')
    return headers


def _html_headers():
    headers = dict()
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,de;q=0.6'
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'ais.usvisa-info.com'
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    headers['sec-ch-ua'] = 'Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = 'Linux'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-origin'
    return headers


def _form_headers(csrf_token):
    headers = dict()
    headers['X-CSRF-Token'] = csrf_token
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    headers['Accept'] = '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,de;q=0.6'
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'ais.usvisa-info.com'
    headers['Origin'] = 'https://ais.usvisa-info.com'
    headers['Referer'] = 'https://ais.usvisa-info.com/en-am/niv/users/sign_in'
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    headers['X-Requested-With'] = 'XMLHttpRequest'
    headers['sec-ch-ua'] = 'Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = 'Linux'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-origin'
    return headers
