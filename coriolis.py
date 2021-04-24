import base64
import gzip
import json
import io
import requests


def encode_loadout_event(loadout_event: dict) -> str:

    string = json.dumps(loadout_event, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(string)

    return base64.urlsafe_b64encode(out.getvalue()).decode().replace("=", "%3D")


def get_coriolis_url(loadout_event: dict) -> str:
    return f"https://coriolis.io/import?data={encode_loadout_event(loadout_event)}"


def convert_loadout_event_to_coriolis(loadout_event: dict) -> str:
    response = requests.post("https://coriolis-api.gobidev.de/convert", json=loadout_event)
    return response.text
