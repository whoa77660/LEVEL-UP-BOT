import os
import requests
import urllib3
from google_play_scraper import app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ggblueshark.com is the replacement for decommissioned ggbluefox.com (new since 2024-03-27).
# Override either URL via environment variable if Garena changes domains again.
_DEFAULT_BD_LOGIN_URL  = "https://clientbp.ggpolarbear.com/"
_DEFAULT_IND_LOGIN_URL = "https://loginbp.ggpolarbear.com/"

BD_LOGIN_URL  = os.getenv("BD_LOGIN_URL",  _DEFAULT_BD_LOGIN_URL)
IND_LOGIN_URL = os.getenv("IND_LOGIN_URL", _DEFAULT_IND_LOGIN_URL)

def AuToUpDaTE():
    version = "1.123.8"
    ob = "OB53"
    try:
        result = app('com.dts.freefireth', lang="fr", country='fr')
        version = result['version']
    except Exception:
        pass

    bd_url = BD_LOGIN_URL  # start with env / default

    # Try the live version API on ggblueshark.com (replacement for ggbluefox.com).
    # If it responds, use its server_url so we always have the freshest value.
    for api_host in ("bdversion.ggblueshark.com", "bdversion.ggbluefox.com"):
        try:
            r = requests.get(
                f'https://{api_host}/live/ver.php?version={version}&lang=ar&device=android'
                '&channel=android&appstore=googleplay&region=ME&whitelist_version=1.3.0'
                '&whitelist_sp_version=1.0.0&device_name=google%20G011A'
                '&device_CPU=ARMv7%20VFPv3%20NEON%20VMH'
                '&device_GPU=Adreno%20(TM)%20640&device_mem=1993',
                verify=False,
                timeout=5
            ).json()
            fetched = r.get('server_url', '')
            if fetched and fetched.startswith('http'):
                bd_url = fetched if fetched.endswith('/') else fetched + '/'
            ob = r.get('latest_release_version', ob)
            break   # success — no need to try the fallback host
        except Exception:
            continue  # try next host

    # Allow a hard env-var override to win over whatever the API returned.
    bd_url = os.getenv("BD_LOGIN_URL", bd_url)

    return bd_url, IND_LOGIN_URL, ob, version
