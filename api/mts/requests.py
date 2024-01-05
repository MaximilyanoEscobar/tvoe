import json
import logging
import random
import string
from urllib import parse

import aiohttp
from aiohttp import ClientError

from api.mts.models import BaseRequestModel


class BaseRequest(object):
    def __init__(self,
                 base_url: str,
                 headers: dict = None,
                 proxy: str = None):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36',
        } if headers is None else headers
        self.proxy = proxy
        self.debug = True

    async def _request(self, method, endpoint, **params) -> BaseRequestModel:
        url = f"{self.base_url}/{endpoint}"
        try:
            if self.debug:
                dict_params = {**params}
                print(f'[DEBUG] Request URL: {url} Params: {dict_params}')
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers,
                                           proxy=self.proxy, **params) as response:
                    response.raise_for_status()
                    if self.debug:
                        print(f'[DEBUG] Response URL: {url} Response: {await response.text()}')
                    return BaseRequestModel(text=await response.text(encoding="utf-8"), status_code=response.status)

        except ClientError as e:
            logging.error(f"Error during API request: {e}")
            raise  # Re-raise the exception


class TvoeAPI(BaseRequest):
    def __init__(self, base_url='https://api.mindbox.ru'):
        super().__init__(base_url=base_url)

    async def create_integration(self,
                                 email: str,
                                 result_in_wheel: int
                                 ):
        endpoint = 'v3/js/operations/async'
        params = {
            'version': '1.0.524',
            'transactionId': 'd607d215-beaf-4a53-b125-04d4452cbd2e',
            'transport': 'beacon',
            'operation': 'popmechanic-integration-create-76921',
            'originDomain': 'tvoe.ru',
        }
        second_data = {
                "customer": {
                    "email": email,
                    "firstName": "Евгений",
                    "subscriptions": [
                        {
                            "pointOfContact": "Email"
                        }
                    ]
                },
                "customerAction": {
                    "customFields": {
                        "EmailInWheel": email,
                        "WinResultlInWheel": result_in_wheel
                    }
                }
            }
        data = {
            "version": "1.0.524",
            "transactionId": "d607d215-beaf-4a53-b125-04d4452cbd2e",
            "transport": "beacon",
            "operation": "popmechanic-integration-create-76921",
            "originDomain": "tvoe.ru",
            "deviceUUID": "78c87e96-c1e6-42ca-a739-db3491168b5e",
            "ianaTimeZone": "Europe/Moscow",
            "data": str(second_data)
        }


        return await self._request('POST', endpoint, params=params, data=data)
