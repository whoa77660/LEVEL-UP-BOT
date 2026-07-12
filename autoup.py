import requests
import urllib3
from google_play_scraper import app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Known working login servers per region
BD_LOGIN_URL  = "https://loginbp.ggbluefox.com/"
IND_LOGIN_URL = "https://loginbp.ggpolarbear.com/"

def AuToUpDaTE():
    version = "1.123.8"
    ob = "OB53"
    try:
        result = app('com.dts.freefireth', lang="fr", country='fr')
        version = result['version']
    except Exception:
        pass

    # Try to confirm BD URL from the live version API
    # Try to get the live server URL from the version API.
    # If unreachable, fall back to the known-working IND server
    # (Free Fire allows BD accounts to authenticate via it).
    bd_url = IND_LOGIN_URL
    try:
        r = requests.get(
            f'https://bdversion.ggbluefox.com/live/ver.php?version={version}&lang=ar&device=android'
            '&channel=android&appstore=googleplay&region=ME&whitelist_version=1.3.0'
            '&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH'
            '&device_GPU=Adreno%20(TM)%20640&device_mem=1993',
            verify=False,
            timeout=5
        ).json()
        fetched = r.get('server_url', '')
        if fetched and fetched.startswith('http'):
            bd_url = fetched
            if not bd_url.endswith('/'):
                bd_url += '/'
        ob = r.get('latest_release_version', ob)
    except Exception:
        pass

    return bd_url, IND_LOGIN_URL, ob, version
