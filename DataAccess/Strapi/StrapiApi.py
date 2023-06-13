import json
import requests


class StrapiApi:
    TOKEN = "3bcc243c7927bfd047f6af4e5e9c9fdc274ecaa750569a9233b597a32cc9c2c4118fbd97b13033866f893bcf283a6cb90596c413ab1ca48eb74499089f82baf9f22444ebfce48af3b8d0bf2fa9ae39daed807644524735770a8ab8034fead9e95a85ed92437d1eacae19c6a4342f841a36d58fe38e52278331870b1983493956"

    def __init__(self, url: str) -> None:
        self._headers = {"Authorization": f"Bearer {StrapiApi.TOKEN}"}
        self._url = url

    def get(self, path: str) -> any:
        response = requests.get(self._url + path, headers=self._headers)
        return response.json()["data"]

    def post(self, path: str, data: "list[any]") -> any:
        response = requests.post(
            self._url + path,
            json={"data": data},
            headers=self._headers,
        )
        response.raise_for_status()
        return response.json()["data"]
