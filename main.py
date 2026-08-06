# ⚡ FF AUTO LEVEL UP BOT – RNR TEAM ⚡
# Firebase + .env + Graceful shutdown + Keep-alive + Debug Console

import os
import json
import asyncio
import signal
import time
import ssl
import urllib3
import threading
import requests
import collections
import random

from datetime import datetime

import aiohttp
from aiohttp import web
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, db

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from xDL import *
from autoup import AuToUpDaTE
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2
import google.protobuf.json_format as json_format

# ─── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()
ADMIN_PASSWORD        = os.getenv("ADMIN_PASSWORD", "rnr6677")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_KEY_JSON     = os.getenv("FIREBASE_KEY_JSON")

if not FIREBASE_KEY_JSON:
    raise RuntimeError("Missing FIREBASE_KEY_JSON environment variable")

# ─── Firebase ─────────────────────────────────────────────────────────────────
firebase_credentials = None
if FIREBASE_KEY_JSON:
    try:
        firebase_credentials = json.loads(FIREBASE_KEY_JSON)
    except Exception as exc:
        clog("ERROR", "startup", f"⚠️ Failed to parse FIREBASE_KEY_JSON: {exc}")

if not firebase_credentials:
    firebase_file = os.path.join(os.path.dirname(__file__), 'firebase.json')
    if os.path.exists(firebase_file):
        with open(firebase_file, 'r', encoding='utf-8') as fh:
            firebase_credentials = json.load(fh)

if not firebase_credentials:
    raise RuntimeError("Missing Firebase credentials. Provide FIREBASE_KEY_JSON or firebase.json")

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})

ref_root   = db.reference('/')
ref_bots   = ref_root.child('bots')
ref_queues = ref_root.child('queues')
ref_active = ref_root.child('active_sessions')

# ─── Global console log buffer ────────────────────────────────────────────────
_LOG_BUFFER  = collections.deque(maxlen=1000)
_LOG_COUNTER = [0]
_LOG_LOCK    = threading.Lock()

def clog(tag: str, uid, msg: str, data: str = ""):
    """Thread-safe console log. Stores to buffer + prints."""
    ts  = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    idx = _LOG_COUNTER[0]
    entry = {
        "i":    idx,
        "ts":   ts,
        "tag":  tag.upper()[:8],
        "uid":  str(uid)[:14],
        "msg":  msg,
        "data": data[:300]
    }
    with _LOG_LOCK:
        _LOG_BUFFER.append(entry)
        _LOG_COUNTER[0] += 1
    data_part = f" | {data[:100]}" if data else ""
    print(f"[{ts}][{tag:<8s}][{str(uid):<13s}] {msg}{data_part}")

# ─── Configuration ────────────────────────────────────────────────────────────
START_SPAM_DURATION   = 20
WAIT_AFTER_MATCH      = 1
LOADING_EXTRA         = 1
START_SPAM_DELAY      = 0.1
MATCH_DETECT_TIMEOUT  = 30
MATCH_DETECT_MIN_SIZE = 10

PACKET_TYPE_BD      = "0519"
PACKET_TYPE_IND     = "0515"
PACKET_TYPE_DEFAULT = "0515"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def rot13(text):
    result = ""
    for c in text:
        if 'a' <= c <= 'z':
            result += chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            result += chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += c
    return result

LEVEL_UP = "RNR TEAM"

async def SEndPacKeT(ChaT, OnLinE, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        ChaT.write(PacKeT)
        await ChaT.drain()
    elif TypE == 'OnLine' and OnLinE:
        OnLinE.write(PacKeT)
        await OnLinE.drain()

async def GeNeRaTeAccEss(uid, password):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    clog("OAUTH", uid, f"→ POST {url}")
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                clog("OAUTH", uid, f"← HTTP {response.status}")
                if response.status == 200:
                    rdata = await response.json()
                    open_id      = rdata.get("open_id")
                    access_token = rdata.get("access_token")
                    if open_id:
                        clog("OAUTH", uid, f"✅ OK open_id={open_id}")
                    else:
                        clog("OAUTH", uid, "❌ No open_id in response", str(rdata)[:200])
                    return open_id, access_token
                else:
                    body = await response.text()
                    clog("ERROR", uid, f"❌ OAuth FAIL HTTP {response.status}", body[:200])
                    return None, None
    except Exception as e:
        clog("ERROR", uid, f"❌ OAuth exception: {e}")
        return None, None

# ─── Fetch version + login URLs ───────────────────────────────────────────────
BD_LOGIN_URL, IND_LOGIN_URL, ob, version = AuToUpDaTE()
_bd_src  = "(env)" if os.environ.get("BD_LOGIN_URL")  else "(auto)"
_ind_src = "(env)" if os.environ.get("IND_LOGIN_URL") else "(auto)"
clog("INFO", "startup", f"BD  Login: {BD_LOGIN_URL} {_bd_src}")
clog("INFO", "startup", f"IND Login: {IND_LOGIN_URL} {_ind_src}")
clog("INFO", "startup", f"Version : {version}  OB: {ob}")

Hr = {
    'User-Agent': Uaa(),
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': ob
}

async def encrypted_proto(encoded_hex):
    key    = b'Yg&tc%DEuh6%Zc^8'
    iv     = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(encoded_hex, AES.block_size)
    return cipher.encrypt(padded)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time        = str(datetime.now())[:-7]
    major_login.game_name         = "free fire"
    major_login.platform_id       = 2
    try:
        major_login.client_version    = version
    except NameError:
        major_login.client_version    = "1.126.2"
    major_login.system_software   = "Android OS 11 / API-30 (RQ3A.210805.001)"
    major_login.system_hardware   = "Handheld"
    major_login.telecom_operator  = "Verizon"
    major_login.network_type      = "WIFI"
    major_login.screen_width      = 1080
    major_login.screen_height     = 2400
    major_login.screen_dpi        = "440"
    major_login.processor_details = "ARMv8"
    major_login.memory            = 6144
    major_login.gpu_renderer      = "Adreno (TM) 650"
    major_login.gpu_version       = "OpenGL ES 3.2 V@1.50"
    major_login.unique_device_id  = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip         = ""
    major_login.language          = "en"
    major_login.open_id           = open_id
    major_login.open_id_type      = "4"
    major_login.device_type       = "Handheld"
    mem = major_login.memory_available
    mem.version      = 55
    mem.hidden_value = 81
    major_login.access_token          = access_token
    major_login.platform_sdk_id       = 2
    major_login.network_operator_a    = "Verizon"
    major_login.network_type_a        = "WIFI"
    major_login.client_using_version  = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total        = 128512
    major_login.external_storage_available    = random.randint(38000, 52000)
    major_login.internal_storage_total        = 110731
    major_login.internal_storage_available    = random.randint(18000, 32000)
    major_login.game_disk_storage_total       = 26628
    major_login.game_disk_storage_available   = random.randint(18000, 25000)
    major_login.external_sdcard_total_storage = 119234
    major_login.external_sdcard_avail_storage = random.randint(25000, 60000)
    major_login.login_by          = 3
    major_login.library_path      = "/data/app/~~random/base.apk"
    major_login.reg_avatar        = 1
    major_login.library_token     = "hash|base.apk"
    major_login.channel_type      = 3
    major_login.cpu_type          = 2
    major_login.cpu_architecture  = "64"
    major_login.client_version_code    = "2024010012"
    major_login.graphics_api          = "OpenGLES3"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type    = 4
    major_login.analytics_detail      = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time          = random.randint(9000, 18000)
    major_login.release_channel       = "android"
    major_login.if_push              = 1
    major_login.is_vpn               = 0
    major_login.android_engine_init_flag = 110009
    major_login.origin_platform_type  = "4"
    major_login.primary_platform_type = "4"
    return await encrypted_proto(major_login.SerializeToString())

async def MajorLogin(payload, login_url, bot_uid="bot"):
    # Use canonical loginbp hosts similar to the TCP bot, with sensible fallbacks.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode    = ssl.CERT_NONE

    async def _post_raw(url):
        clog("LOGIN", bot_uid, f"→ POST {url} payload={len(payload)}B", payload.hex()[:64])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
                    clog("LOGIN", bot_uid, f"← HTTP {response.status} from {url}")
                    if response.status == 200:
                        data = await response.read()
                        clog("LOGIN", bot_uid, f"✅ MajorLogin OK resp={len(data)}B", data.hex()[:64])
                        return data
                    body = await response.text()
                    clog("ERROR", bot_uid, f"❌ MajorLogin HTTP {response.status} from {url}", body[:300])
                    return None
        except Exception as e:
            clog("ERROR", bot_uid, f"❌ MajorLogin exception for {url}: {e}")
            return None

    candidates = []
    # Prefer loginbp matching the detected base domain
    if login_url:
        if 'ggblueshark' in login_url:
            candidates.append('https://loginbp.ggblueshark.com/MajorLogin')
        if 'ggpolarbear' in login_url:
            candidates.append('https://loginbp.ggpolarbear.com/MajorLogin')
        # If login_url looks like clientbp, try its loginbp counterpart
        if 'clientbp' in login_url:
            candidates.append(login_url.replace('clientbp', 'loginbp').rstrip('/') + '/MajorLogin')

    # Add canonical fallbacks
    candidates.extend([
        'https://loginbp.ggblueshark.com/MajorLogin',
        'https://loginbp.ggpolarbear.com/MajorLogin'
    ])

    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)

    for url in uniq:
        resp = await _post_raw(url)
        if resp:
            return resp

    return None

async def GetLoginData(base_url, payload, token, bot_uid="bot"):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode    = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    clog("LOGIN", bot_uid, f"→ GetLoginData {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
                clog("LOGIN", bot_uid, f"← GetLoginData HTTP {response.status}")
                if response.status == 200:
                    return await response.read()
                return None
    except Exception as e:
        clog("ERROR", bot_uid, f"❌ GetLoginData exception: {e}")
        return None

async def DecRypTMajoRLoGin(data):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(data)
    return proto

async def DecRypTLoGinDaTa(data):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(data)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto  = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex    = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp     = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet        = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9:    headers = '0000000'
    elif uid_length == 8:  headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7:  headers = '000000000'
    else:                  headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def join_teamcode_packet(team_code, key, iv, region):
    fields = {
        1: 4,
        2: {
            4: bytes.fromhex("01090a0b121920"),
            5: str(team_code),
            6: 6,
            8: 1,
            9: {2: 800, 6: 11, 8: "1.111.1", 9: 5, 10: 1}
        }
    }
    ptype = PACKET_TYPE_BD if region.upper() == "BD" else (PACKET_TYPE_IND if region.upper() == "IND" else PACKET_TYPE_DEFAULT)
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), ptype, key, iv)

async def start_auto_packet(key, iv, region):
    fields = {1: 9, 2: {1: 12480598706}}
    ptype  = PACKET_TYPE_BD if region.upper() == "BD" else (PACKET_TYPE_IND if region.upper() == "IND" else PACKET_TYPE_DEFAULT)
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), ptype, key, iv)

async def leave_squad_packet(key, iv, region):
    fields = {1: 7, 2: {1: 12480598706}}
    ptype  = PACKET_TYPE_BD if region.upper() == "BD" else (PACKET_TYPE_IND if region.upper() == "IND" else PACKET_TYPE_DEFAULT)
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), ptype, key, iv)

# ─── Bot auto-start loop ──────────────────────────────────────────────────────
async def bot_auto_start_loop(team_code, online_writer, whisper_writer, key, iv,
                               region, stop_event, bot_instance, match_started_event):
    uid = bot_instance.uid
    while not stop_event.is_set():
        try:
            join_pkt = await join_teamcode_packet(team_code, key, iv, region)
            clog("SEND", uid, f"→ JOIN team={team_code} region={region}", join_pkt.hex()[:64])
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
            await asyncio.sleep(2)

            match_started_event.clear()
            start_pkt  = await start_auto_packet(key, iv, region)
            spam_end   = time.time() + START_SPAM_DURATION
            spam_count = 0
            clog("SEND", uid, f"▶ START spam begin team={team_code} ({START_SPAM_DURATION}s)")
            while time.time() < spam_end and not stop_event.is_set() and not match_started_event.is_set():
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', start_pkt)
                spam_count += 1
                await asyncio.sleep(START_SPAM_DELAY)
            clog("SEND", uid, f"▶ START spam done — sent {spam_count} packets")

            if stop_event.is_set():
                break

            start_wait = time.time()
            while not stop_event.is_set():
                if match_started_event.is_set():
                    break
                if time.time() - start_wait >= MATCH_DETECT_TIMEOUT:
                    clog("BOT", uid, f"⏰ No match in {MATCH_DETECT_TIMEOUT}s → leaving squad")
                    leave_pkt = await leave_squad_packet(key, iv, region)
                    clog("SEND", uid, "→ LEAVE squad", leave_pkt.hex()[:64])
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_pkt)
                    await asyncio.sleep(2)
                    return
                await asyncio.sleep(1)

            if stop_event.is_set():
                break

            clog("BOT", uid, f"🎮 Match detected! Waiting {WAIT_AFTER_MATCH + LOADING_EXTRA}s for level-up")
            await asyncio.sleep(WAIT_AFTER_MATCH + LOADING_EXTRA)

            if stop_event.is_set():
                break

            leave_pkt = await leave_squad_packet(key, iv, region)
            clog("SEND", uid, "→ LEAVE squad after match", leave_pkt.hex()[:64])
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_pkt)
            await asyncio.sleep(2)
            clog("BOT", uid, f"✅ Cycle complete for team={team_code}")

        except Exception as e:
            clog("ERROR", uid, f"Loop error: {e}")
            return

# ─── BotInstance ──────────────────────────────────────────────────────────────
class BotInstance:
    def __init__(self, uid, password, region):
        self.uid        = str(uid)
        self.password   = password
        self.region     = region.upper()   # always normalise
        self.login_url  = BD_LOGIN_URL if self.region == "BD" else IND_LOGIN_URL
        self.online_writer  = None
        self.whisper_writer = None
        self.key   = None
        self.iv    = None
        self.stop_event          = None
        self.match_started_event = None
        self.online_task = None
        self.chat_task   = None
        self.ready              = False
        self.current_job_task   = None
        self.current_team       = None
        self.is_busy            = False
        self.current_session_id = None
        self.last_error         = None
        self.account_name      = None

    async def login_and_connect(self):
        clog("BOT", self.uid, f"🔐 Login attempt region={self.region} url={self.login_url}")
        open_id, access_token = await GeNeRaTeAccEss(self.uid, self.password)
        if not open_id:
            self.last_error = "OAuth failed – check UID/password"
            clog("ERROR", self.uid, f"❌ {self.last_error}")
            return False

        payload    = await EncRypTMajoRLoGin(open_id, access_token)
        login_resp = await MajorLogin(payload, self.login_url, self.uid)
        if not login_resp:
            self.last_error = f"MajorLogin failed (503 or connection error) on {self.login_url}"
            clog("ERROR", self.uid, f"❌ {self.last_error}")
            return False

        auth  = await DecRypTMajoRLoGin(login_resp)
        token = auth.token
        if not token:
            self.last_error = "No token in MajorLogin response (banned/region mismatch?)"
            clog("ERROR", self.uid, f"❌ {self.last_error}")
            return False

        url       = auth.url
        self.key  = auth.key
        self.iv   = auth.iv
        timestamp = auth.timestamp
        clog("LOGIN", self.uid, f"✅ MajorLogin OK — token={token[:20]}... game_url={url}")

        login_data = await GetLoginData(url, payload, token, self.uid)
        if not login_data:
            self.last_error = "GetLoginData failed"
            clog("ERROR", self.uid, f"❌ {self.last_error}")
            return False

        ports      = await DecRypTLoGinDaTa(login_data)
        if hasattr(ports, 'AccountName'):
            self.account_name = ports.AccountName
        online_ip, online_port = ports.Online_IP_Port.split(":")
        chat_ip,   chat_port   = ports.AccountIP_Port.split(":")
        clog("CONN", self.uid, f"Game servers → online={online_ip}:{online_port}  chat={chat_ip}:{chat_port}")

        auth_token = await xAuThSTarTuP(int(auth.account_uid), token, int(timestamp), self.key, self.iv)

        self.stop_event          = asyncio.Event()
        self.match_started_event = asyncio.Event()

        async def online_loop():
            while not self.stop_event.is_set():
                try:
                    clog("CONN", self.uid, f"→ Connecting online socket {online_ip}:{online_port}")
                    reader, writer = await asyncio.open_connection(online_ip, int(online_port))
                    self.online_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    clog("CONN", self.uid, "✅ Online socket connected — auth packet sent")
                    while not self.stop_event.is_set():
                        data = await reader.read(9999)
                        if not data:
                            clog("CONN", self.uid, "Online socket closed by server")
                            break
                        clog("RECV", self.uid, f"← ONLINE {len(data)}B", data.hex()[:128])
                        if len(data) > MATCH_DETECT_MIN_SIZE:
                            clog("BOT", self.uid, f"🎮 Match packet detected ({len(data)}B)!")
                            self.match_started_event.set()
                    writer.close()
                    await writer.wait_closed()
                    self.online_writer = None
                    break
                except Exception as e:
                    clog("ERROR", self.uid, f"Online socket error: {e}")
                    await asyncio.sleep(5)

        async def chat_loop():
            while not self.stop_event.is_set():
                try:
                    clog("CONN", self.uid, f"→ Connecting chat socket {chat_ip}:{chat_port}")
                    reader, writer = await asyncio.open_connection(chat_ip, int(chat_port))
                    self.whisper_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    clog("CONN", self.uid, "✅ Chat socket connected — auth packet sent")
                    if hasattr(ports, 'Clan_ID') and ports.Clan_ID:
                        clan_pkt = await AuthClan(ports.Clan_ID, ports.Clan_Compiled_Data, self.key, self.iv)
                        writer.write(clan_pkt)
                        await writer.drain()
                        clog("SEND", self.uid, "→ Clan auth packet sent")
                    while not self.stop_event.is_set():
                        try:
                            data = await asyncio.wait_for(reader.read(9999), timeout=5.0)
                            if data:
                                clog("RECV", self.uid, f"← CHAT {len(data)}B", data.hex()[:128])
                        except asyncio.TimeoutError:
                            pass
                    writer.close()
                    await writer.wait_closed()
                    self.whisper_writer = None
                    break
                except Exception as e:
                    clog("ERROR", self.uid, f"Chat socket error: {e}")
                    await asyncio.sleep(5)

        if self.online_task:
            self.online_task.cancel()
        if self.chat_task:
            self.chat_task.cancel()
        self.online_task = asyncio.create_task(online_loop())
        self.chat_task   = asyncio.create_task(chat_loop())
        await asyncio.sleep(3)
        self.ready      = True
        self.last_error = None
        clog("BOT", self.uid, f"✅ Bot READY region={self.region}")
        return True

    async def reconnect(self):
        clog("BOT", self.uid, "🔄 Reconnecting...")
        self.ready = False
        if self.stop_event:
            self.stop_event.set()
        if self.current_job_task and not self.current_job_task.done():
            self.current_job_task.cancel()
        self.is_busy            = False
        self.current_team       = None
        self.current_session_id = None
        if self.online_writer:
            self.online_writer.close()
        if self.whisper_writer:
            self.whisper_writer.close()
        if self.online_task:
            self.online_task.cancel()
        if self.chat_task:
            self.chat_task.cancel()
        await asyncio.sleep(1)
        success = await self.login_and_connect()
        if not success:
            clog("ERROR", self.uid, "❌ Reconnect FAILED")
            self.ready = False
        else:
            clog("BOT", self.uid, "✅ Reconnect successful")
            self.ready = True

    async def start_job(self, team_code, mgr, session_id):
        if not self.ready or self.is_busy:
            return
        self.is_busy            = True
        self.current_team       = team_code
        self.current_session_id = session_id
        self.stop_event.clear()
        self.match_started_event.clear()
        clog("BOT", self.uid, f"▶ Job started team={team_code} session={session_id[:8]}")
        self.current_job_task = asyncio.create_task(
            bot_auto_start_loop(team_code, self.online_writer, self.whisper_writer,
                                self.key, self.iv, self.region, self.stop_event,
                                self, self.match_started_event)
        )
        try:
            await self.current_job_task
        except asyncio.CancelledError:
            pass
        self.is_busy            = False
        self.current_team       = None
        self.current_session_id = None
        clog("BOT", self.uid, f"✅ Job finished team={team_code}")
        await mgr.bot_finished(self)

    async def stop_job(self):
        if self.stop_event:
            self.stop_event.set()
        if self.match_started_event:
            self.match_started_event.clear()
        if self.current_job_task and not self.current_job_task.done():
            self.current_job_task.cancel()
        await asyncio.sleep(0.5)
        await self.reconnect()

    async def disconnect(self):
        if self.stop_event:
            self.stop_event.set()
        if self.online_task:
            self.online_task.cancel()
        if self.chat_task:
            self.chat_task.cancel()
        if self.online_writer:
            self.online_writer.close()
        if self.whisper_writer:
            self.whisper_writer.close()
        self.ready = False

# ─── QueueManager ─────────────────────────────────────────────────────────────
class QueueManager:
    def __init__(self):
        self.bots        = []
        self.bot_dict    = {}
        self.failed_bots = []   # list of {uid, region, error, ts}

    async def init_from_firebase(self):
        clog("FIREBASE", "manager", "📡 Loading bots from Firebase bots/ node...")
        try:
            bots_data = await asyncio.to_thread(ref_bots.get)
        except Exception as e:
            clog("ERROR", "manager", f"❌ Firebase read error: {e}")
            return

        if not bots_data:
            clog("FIREBASE", "manager", "⚠️  No bots found in Firebase (bots/ is empty)")
            return

        clog("FIREBASE", "manager", f"Found {len(bots_data)} bot record(s)")
        for uid, data in bots_data.items():
            if not isinstance(data, dict):
                clog("FIREBASE", uid, f"⚠️  Unexpected data format: {type(data).__name__} = {data}")
                continue
            pwd    = data.get('password', '')
            region = data.get('region', 'BD')
            if not pwd:
                clog("ERROR", uid, "⚠️  No password field in Firebase for this bot — skipping")
                self.failed_bots.append({
                    'uid': uid, 'region': region,
                    'error': 'No password in Firebase record',
                    'ts': datetime.now().strftime("%H:%M:%S")
                })
                continue
            bot     = BotInstance(uid, pwd, region)
            success = await bot.login_and_connect()
            if success:
                self.bots.append(bot)
                self.bot_dict[uid] = bot
                await asyncio.to_thread(ref_bots.child(uid).update, {'ready': True})
            else:
                self.failed_bots.append({
                    'uid': uid, 'region': region,
                    'error': bot.last_error or 'Unknown error',
                    'ts': datetime.now().strftime("%H:%M:%S")
                })
        clog("BOT", "manager",
             f"🎉 Loading done — {len(self.bots)} online, {len(self.failed_bots)} failed")

    async def add_bot(self, uid, password, region):
        bot = BotInstance(uid, password, region)
        if await bot.login_and_connect():
            self.bots.append(bot)
            self.bot_dict[uid] = bot
            self.failed_bots = [f for f in self.failed_bots if f['uid'] != uid]
            await asyncio.to_thread(ref_bots.child(uid).set, {
                'password': password, 'region': region,
                'ready': True, 'busy': False,
                'current_team': None, 'current_session_id': None
            })
            return True, "Bot added and connected"
        else:
            return False, bot.last_error or "Login failed"

    async def remove_bot(self, uid):
        bot = self.bot_dict.get(uid)
        if bot:
            await bot.disconnect()
            self.bots.remove(bot)
            del self.bot_dict[uid]
            await asyncio.to_thread(ref_bots.child(uid).delete)
        else:
            self.failed_bots = [f for f in self.failed_bots if f['uid'] != uid]
        return True

    async def add_request(self, team_code, session_id, region):
        active_data = await asyncio.to_thread(ref_active.child(session_id).get)
        if active_data:
            return {'status': 'error', 'message': 'You already have a bot running. Stop it first.'}
        region_up = region.upper()
        for bot in self.bots:
            if bot.ready and not bot.is_busy and bot.region == region_up:
                await asyncio.to_thread(ref_active.child(session_id).set, {
                    'bot_uid': bot.uid, 'region': region_up,
                    'team_code': team_code,
                    'started_at': datetime.now().isoformat()
                })
                asyncio.create_task(bot.start_job(team_code, self, session_id))
                return {'status': 'started', 'bot_uid': bot.uid, 'queue_position': 0}
        queue_ref = ref_queues.child(region_up)
        await asyncio.to_thread(queue_ref.push, {'team_code': team_code, 'session_id': session_id})
        q = await asyncio.to_thread(queue_ref.get)
        return {'status': 'queued', 'queue_position': len(q) if q else 1}

    async def stop_request(self, session_id):
        active_data = await asyncio.to_thread(ref_active.child(session_id).get)
        if active_data:
            bot = self.bot_dict.get(active_data['bot_uid'])
            if bot:
                await bot.stop_job()
            await asyncio.to_thread(ref_active.child(session_id).delete)
            return {'status': 'stopped', 'message': 'Bot stopped and reconnecting'}
        for region in ['BD', 'IND']:
            queue_ref = ref_queues.child(region)
            q_data = await asyncio.to_thread(queue_ref.get)
            if q_data:
                for key, entry in q_data.items():
                    if entry.get('session_id') == session_id:
                        await asyncio.to_thread(queue_ref.child(key).delete)
                        return {'status': 'stopped', 'message': 'Removed from queue'}
        return {'status': 'error', 'message': 'No active or queued job for this session'}

    async def bot_finished(self, bot):
        active_sessions = await asyncio.to_thread(ref_active.get)
        if active_sessions:
            for sid, data in active_sessions.items():
                if data.get('bot_uid') == bot.uid:
                    await asyncio.to_thread(ref_active.child(sid).delete)
                    break
        region    = bot.region
        queue_ref = ref_queues.child(region)
        q = await asyncio.to_thread(queue_ref.get)
        if q:
            first_key  = next(iter(q))
            entry      = q[first_key]
            team_code  = entry['team_code']
            session_id = entry['session_id']
            for b in self.bots:
                if b.ready and not b.is_busy and b.region == region:
                    await asyncio.to_thread(ref_active.child(session_id).set, {
                        'bot_uid': b.uid, 'region': region,
                        'team_code': team_code,
                        'started_at': datetime.now().isoformat()
                    })
                    asyncio.create_task(b.start_job(team_code, self, session_id))
                    await asyncio.to_thread(queue_ref.child(first_key).delete)
                    break

    async def get_status(self):
        bots_status = [{
            'uid': b.uid, 'region': b.region,
            'busy': b.is_busy,
            'current_team': b.current_team if b.is_busy else None,
            'ready': b.ready
        } for b in self.bots]
        bd_queue  = await asyncio.to_thread(ref_queues.child('BD').get)  or {}
        ind_queue = await asyncio.to_thread(ref_queues.child('IND').get) or {}
        return {
            'bots': bots_status,
            'failed': self.failed_bots,
            'queues': {
                'BD':  [{'team_code': v['team_code'], 'session_id': v['session_id'][:8]} for v in bd_queue.values()],
                'IND': [{'team_code': v['team_code'], 'session_id': v['session_id'][:8]} for v in ind_queue.values()]
            }
        }

    def get_bots_list(self):
        return [{
            'uid': b.uid, 'name': b.account_name or '', 'region': b.region,
            'ready': b.ready, 'busy': b.is_busy,
            'error': b.last_error
        } for b in self.bots]

# ─── Global manager ───────────────────────────────────────────────────────────
manager = QueueManager()

# ─── Main page ────────────────────────────────────────────────────────────────
async def handle_index(request):
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF AUTO LEVEL UP BOT | RNR TEAM</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Poppins',system-ui,'Segoe UI',Roboto,sans-serif; }
        body { min-height:100vh; background:linear-gradient(135deg,#0a0f1e 0%,#0a1a2a 100%); display:flex; justify-content:center; align-items:center; padding:20px; }
        .glass-card { background:rgba(15,25,45,0.85); backdrop-filter:blur(12px); border-radius:2rem; border:1px solid rgba(0,255,255,0.4); box-shadow:0 25px 45px rgba(0,0,0,0.3),0 0 20px rgba(0,255,255,0.2); padding:2rem; width:100%; max-width:800px; }
        h1 { font-size:2rem; font-weight:700; background:linear-gradient(135deg,#00f2fe,#4facfe); -webkit-background-clip:text; background-clip:text; color:transparent; text-align:center; margin-bottom:0.25rem; }
        .credit { text-align:center; font-size:0.8rem; color:#88aaff; margin-bottom:0.5rem; }
        .credit a { color:cyan; text-decoration:none; }
        .sub { display:block; text-align:center; color:#b8e2ff; margin-bottom:1.5rem; font-size:0.8rem; }
        .region-toggle { display:flex; gap:15px; justify-content:center; margin-bottom:25px; }
        .region-btn { background:rgba(0,0,0,0.5); border:2px solid #00aaff; border-radius:60px; padding:10px 30px; font-weight:bold; cursor:pointer; transition:0.2s; color:white; }
        .region-btn.active { background:linear-gradient(95deg,#00b4db,#0083b0); border-color:white; box-shadow:0 0 12px cyan; }
        .input-group { display:flex; gap:12px; margin-bottom:30px; flex-wrap:wrap; }
        .input-group input { flex:2; min-width:180px; background:rgba(0,0,0,0.6); border:1px solid #00aaff; border-radius:60px; padding:14px 20px; font-size:1rem; color:#fff; outline:none; }
        .input-group input:focus { border-color:#00ffff; box-shadow:0 0 10px rgba(0,255,255,0.5); }
        button { background:linear-gradient(95deg,#00b4db,#0083b0); border:none; border-radius:60px; padding:12px 28px; font-weight:bold; font-size:1rem; color:white; cursor:pointer; transition:transform 0.2s; }
        button:hover { transform:translateY(-2px); }
        .stop-btn { background:linear-gradient(95deg,#d64545,#b12a2a); }
        .status-panel { background:rgba(0,0,0,0.5); border-radius:1.5rem; padding:1.2rem; margin:25px 0; border:1px solid rgba(0,255,255,0.3); }
        .status-panel h3 { color:#fff; margin-bottom:12px; }
        .bot-item { display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid rgba(255,255,255,0.2); gap:10px; flex-wrap:wrap; }
        .bot-uid { font-family:monospace; font-weight:700; background:#0a2a3a; padding:4px 12px; border-radius:40px; font-size:0.9rem; color:white; border:1px solid #00aaff; flex:1; }
        .bot-region { background:#1e3a5f; padding:4px 12px; border-radius:40px; font-size:0.8rem; font-weight:bold; color:cyan; }
        .status-badge { padding:5px 14px; border-radius:40px; font-size:0.8rem; font-weight:bold; }
        .free { background:#1e7e34; color:white; }
        .busy { background:#c0392b; color:white; }
        .reconnecting { background:#f0ad4e; color:black; }
        .queue-section { margin-top:15px; }
        .queue-title { font-size:0.9rem; font-weight:bold; color:cyan; margin:10px 0 5px; }
        .queue-item { background:rgba(0,20,40,0.7); margin:4px 0; padding:6px 12px; border-radius:30px; font-size:0.8rem; display:flex; justify-content:space-between; color:#e0e0e0; border:1px solid rgba(0,200,255,0.3); }
        .loading-status { margin-top:15px; padding:10px; background:rgba(0,0,0,0.4); border-radius:60px; font-size:0.8rem; color:#aaffdd; text-align:center; }
        footer { text-align:center; margin-top:25px; font-size:0.75rem; color:#aaccee; }
        .admin-link { color:#88ddff; text-decoration:none; font-weight:600; }
        .toast { position:fixed; bottom:80px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.85); color:white; padding:12px 24px; border-radius:60px; font-size:0.9rem; font-weight:bold; z-index:1000; border-left:5px solid cyan; }
        .rules-modal { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); display:flex; justify-content:center; align-items:center; z-index:2000; }
        .rules-card { background:rgba(15,25,45,0.95); border-radius:2rem; padding:2rem; max-width:550px; width:90%; border:1px solid cyan; color:white; text-align:center; }
        .rules-card h2 { color:cyan; margin-bottom:1rem; }
        .rules-card h3 { color:#aaaaff; margin:1rem 0 0.5rem; font-size:1rem; }
        .rules-card p { margin:0.5rem 0; line-height:1.4; }
        .rules-card a { color:cyan; }
        .rules-card button { background:cyan; color:black; margin-top:1rem; }
        @media(max-width:550px){ .glass-card{padding:1.5rem;} .input-group{flex-direction:column;} button{width:100%;} }
    </style>
</head>
<body>
<div class="glass-card">
    <h1>⚡ FF AUTO LEVEL UP BOT</h1>
    <div class="credit">🚀 RNR TEAM — <a href="https://t.me/Rahmttollah" target="_blank">@Rahmttollah</a></div>
    <span class="sub">PREMIUM | JUST PUT YOUR TEAM CODE</span>
    <div class="region-toggle">
        <div id="btnBD" class="region-btn active" onclick="setRegion('BD')">🇧🇩 BANGLADESH</div>
        <div id="btnIND" class="region-btn" onclick="setRegion('IND')">🇮🇳 INDIA</div>
    </div>
    <div class="input-group">
        <input type="text" id="teamcode" placeholder="Enter team code (digits only)" inputmode="numeric" autocomplete="off">
        <button id="pasteBtn" type="button" style="background:#2c5a7a;">📋 Paste</button>
        <button id="startBtn">▶ START LEVELING</button>
        <button id="stopBtn" class="stop-btn">⏹ STOP MY BOT</button>
    </div>
    <div class="status-panel">
        <h3>🤖 BOT FLEET STATUS</h3>
        <div id="botsContainer"></div>
        <div class="queue-section">
            <div class="queue-title" id="queueTitle">📋 QUEUE (BANGLADESH)</div>
            <div id="queueList"></div>
        </div>
        <div id="loadingStatus" class="loading-status"></div>
    </div>
    <footer>🔒 Your session is private · <a href="/admin" class="admin-link" target="_blank">Admin Panel</a></footer>
</div>

<div id="rulesModal" class="rules-modal" style="display:none;">
    <div class="rules-card">
        <h2>🚀 FF AUTO LEVEL UP BOT</h2>
        <h3>📌 How to use</h3>
        <p>🇬🇧 Free Fire → Lone Wolf (Dual VS) → Copy Code → Paste → Bot joins & levels up</p>
        <p>🇧🇩 Free Fire খুলুন → Lone Wolf → Code কপি → এখানে দিন → বট জয়েন করবে</p>
        <h3>⚠️ Rules</h3>
        <p>Valid code · Stay online · No spam · Misuse = Ban</p>
        <h3>📢 Support</h3>
        <p><a href="https://t.me/Rahmttollah" target="_blank">t.me/Rahmttollah</a></p>
        <button onclick="document.getElementById('rulesModal').style.display='none'">GOT IT</button>
    </div>
</div>

<script>
    let sessionId = localStorage.getItem('ff_session');
    if (!sessionId) {
        sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{let r=Math.random()*16|0,v=c==='x'?r:(r&0x3|0x8);return v.toString(16);});
        localStorage.setItem('ff_session', sessionId);
    }
    if (!localStorage.getItem('rules_seen')) {
        document.getElementById('rulesModal').style.display = 'flex';
        localStorage.setItem('rules_seen', 'true');
    }
    function showToast(msg, type='info') {
        const t = document.createElement('div');
        t.className = 'toast';
        t.textContent = msg;
        t.style.borderLeftColor = type==='error'?'red':type==='success'?'lime':'cyan';
        document.body.appendChild(t);
        setTimeout(()=>{t.style.opacity='0'; setTimeout(()=>t.remove(),500);}, 3000);
    }
    let currentRegion = 'BD';
    document.getElementById('pasteBtn').addEventListener('click', async()=>{
        try {
            const text = await navigator.clipboard.readText();
            document.getElementById('teamcode').value = text;
            showToast('📋 Pasted','success');
        } catch(e) { showToast('❌ Clipboard access denied','error'); }
    });
    function setRegion(reg) {
        currentRegion = reg;
        document.getElementById('btnBD').classList.toggle('active', reg==='BD');
        document.getElementById('btnIND').classList.toggle('active', reg==='IND');
        document.getElementById('queueTitle').innerText = reg==='BD'?'📋 QUEUE (BANGLADESH)':'📋 QUEUE (INDIA)';
        refreshStatus();
    }
    async function refreshStatus() {
        try {
            const data = await fetch('/status').then(r=>r.json());
            const botsDiv = document.getElementById('botsContainer');
            botsDiv.innerHTML = '';
            const filtered = data.bots.filter(b=>b.region===currentRegion);
            for (let b of filtered) {
                const d = document.createElement('div'); d.className = 'bot-item';
                let sc='', st='';
                if (b.busy) { sc='busy'; st=`BUSY · ${b.current_team}`; }
                else if (!b.ready) { sc='reconnecting'; st='RECONNECTING...'; }
                else { sc='free'; st='FREE'; }
                d.innerHTML = `<span class="bot-uid">${b.uid}</span><span class="bot-region">${b.region}</span><span class="status-badge ${sc}">${st}</span>`;
                botsDiv.appendChild(d);
            }
            if (!filtered.length) botsDiv.innerHTML = '<div class="bot-item">✨ No bots available for this region</div>';
            const ql = document.getElementById('queueList');
            ql.innerHTML = '';
            for (let q of (data.queues[currentRegion]||[])) {
                const item = document.createElement('div'); item.className = 'queue-item';
                item.innerHTML = `<span>🎮 Team ${q.team_code}</span><span>⏳ ${q.session_id}...</span>`;
                ql.appendChild(item);
            }
            if (!(data.queues[currentRegion]||[]).length) ql.innerHTML = '<div class="queue-item">✨ No waiting requests</div>';
            const online = data.bots.filter(b=>b.ready).length;
            const failed = (data.failed||[]).length;
            document.getElementById('loadingStatus').innerHTML =
                `✅ ${online} bots online · ${data.bots.length} total` +
                (failed ? ` · <span style="color:#ff8888">⚠️ ${failed} failed to login</span>` : '');
        } catch(e) { console.warn(e); }
    }
    let autoStartEnabled = true;
    const tc = document.getElementById('teamcode');
    async function autoStartIfReady() {
        const v = tc.value.trim();
        if (autoStartEnabled && v.length===7 && /^\d+$/.test(v)) {
            autoStartEnabled = false;
            document.getElementById('startBtn').click();
            setTimeout(()=>{ autoStartEnabled=true; }, 2000);
        }
    }
    tc.addEventListener('input', autoStartIfReady);
    tc.addEventListener('paste', ()=>{ setTimeout(autoStartIfReady,10); });
    document.getElementById('startBtn').onclick = async()=>{
        const code = tc.value.trim();
        if (!code || !/^\d+$/.test(code)) { showToast('❌ Enter valid numeric team code','error'); return; }
        const data = await fetch('/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({team_code:code,session_id:sessionId,region:currentRegion})}).then(r=>r.json());
        if (data.error) showToast(`❌ ${data.error}`,'error');
        else if (data.queue_position) showToast(`⏳ Queued at #${data.queue_position} (${currentRegion})`,'info');
        else showToast(`✅ Started on bot ${data.bot_uid}`,'success');
        refreshStatus();
    };
    document.getElementById('stopBtn').onclick = async()=>{
        const data = await fetch('/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId})}).then(r=>r.json());
        showToast(data.message||data.error||'Bot stopped', data.error?'error':'success');
        refreshStatus();
    };
    setInterval(refreshStatus, 2500);
    refreshStatus();
</script>
</body>
</html>"""
    return web.Response(text=html, content_type='text/html')

# ─── Admin panel ──────────────────────────────────────────────────────────────
async def handle_admin(request):
    password  = request.query.get('password', '')
    error_msg = request.query.get('error', '')

    if password != ADMIN_PASSWORD:
        err_html = f'<p style="color:#ff6666;margin-top:10px;">❌ {error_msg}</p>' if error_msg else ''
        login_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Login</title><style>
body{{background:#0a0f1e;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;}}
.card{{background:rgba(0,0,0,0.85);padding:2.5rem;border-radius:2rem;border:1px solid cyan;min-width:320px;text-align:center;}}
h2{{color:white;margin-bottom:1.5rem;}}
input{{display:block;width:100%;padding:12px;margin:8px 0;border-radius:40px;border:1px solid cyan;background:#111;color:white;font-size:1rem;text-align:center;}}
button{{width:100%;padding:12px;border-radius:40px;border:none;background:cyan;font-weight:bold;color:black;font-size:1rem;cursor:pointer;margin-top:8px;}}
</style></head>
<body><div class='card'>
<h2>🔐 Admin Access</h2>
<form method='get'>
<input type='password' name='password' placeholder='Enter Admin Password' autofocus>
<button type='submit'>Enter</button>
</form>
{err_html}
</div></body></html>"""
        return web.Response(text=login_html, content_type='text/html')

    bots   = manager.get_bots_list()
    failed = manager.failed_bots

    bots_html = ""
    for b in bots:
        status_color = "#88ff88" if b['ready'] and not b['busy'] else ("#ffaa00" if b['busy'] else "#ff6666")
        status_text  = ("🟢 Ready" if b['ready'] and not b['busy'] else
                        (f"🔴 Busy (team {b.get('current_team','')})" if b['busy'] else "⚠️ Reconnecting"))
        display_name = b['name'] if b.get('name') else b['uid']
        bots_html += f"""
        <div class='bot-card'>
          <span style='color:white;font-weight:bold;font-family:monospace;'>🔹 Name: {display_name}</span>
          <span style='color:#88dfff;'>UID: {b['uid']}</span>
          <span style='color:cyan;'>[{b['region']}]</span>
          <span style='color:{status_color};'>{status_text}</span>
          <button onclick="removeBot('{b['uid']}')" style='background:#c0392b;'>🗑 Remove</button>
        </div>"""

    failed_html = ""
    for f in failed:
        failed_html += f"""
        <div class='bot-card' style='border-color:#ff4444;'>
          <span style='color:#ff8888;font-weight:bold;font-family:monospace;'>{f['uid']}</span>
          <span style='color:cyan;'>[{f['region']}]</span>
          <span style='color:#ff6666;'>❌ {f['error']}</span>
          <span style='color:#888;font-size:0.8rem;'>{f['ts']}</span>
          <button onclick="retryBot('{f['uid']}')" style='background:#2c5a7a;'>🔄 Retry</button>
        </div>"""

    admin_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Panel</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif;}}
body{{background:linear-gradient(145deg,#071a25,#021018);padding:20px;color:#fff;}}
.container{{max-width:900px;margin:auto;background:rgba(0,0,0,0.75);backdrop-filter:blur(8px);border-radius:2rem;padding:2rem;border:1px solid cyan;}}
h1{{text-align:center;color:cyan;margin-bottom:20px;}}
.tabs{{display:flex;gap:10px;margin-bottom:20px;border-bottom:1px solid rgba(0,255,255,0.3);padding-bottom:10px;flex-wrap:wrap;}}
.tab-btn{{background:rgba(0,0,0,0.5);border:1px solid #00aaff;border-radius:40px;padding:8px 20px;cursor:pointer;color:white;transition:0.2s;}}
.tab-btn.active{{background:linear-gradient(95deg,#00b4db,#0083b0);border-color:white;}}
.tab-content{{display:none;}} .tab-content.active{{display:block;}}
.bot-card{{background:#0a1a2e;margin:10px 0;padding:12px 18px;border-radius:60px;display:flex;align-items:center;gap:12px;border:1px solid rgba(0,200,255,0.3);flex-wrap:wrap;}}
button{{background:#2c5a7a;border:none;padding:8px 18px;border-radius:40px;color:white;cursor:pointer;transition:0.2s;}}
button:hover{{background:#00a8cc;}}
.add-section{{background:#01121c;padding:20px;border-radius:1.5rem;margin-top:20px;}}
.add-section h3{{color:#aaffff;margin-bottom:12px;}}
input,select{{background:#102b37;border:1px solid cyan;padding:10px 16px;border-radius:40px;color:white;margin:5px;}}
.console-link{{display:inline-block;background:linear-gradient(95deg,#7b2ff7,#4a1cad);border-radius:40px;padding:10px 24px;color:white;text-decoration:none;font-weight:bold;margin:5px;}}
.msg{{color:#88ff88;margin-top:10px;}}
.err-msg{{color:#ff6666;margin-top:10px;}}
.section-title{{color:#aaffff;font-size:1.1rem;font-weight:bold;margin:15px 0 8px;border-left:3px solid cyan;padding-left:10px;}}
</style>
</head><body>
<div class="container">
<h1>👑 ADMIN DASHBOARD</h1>
<div style="text-align:center;margin-bottom:15px;">
  <a href="/admin/console?password={password}" class="console-link">🖥 Live Debug Console</a>
  <a href="/admin/firebase?password={password}" class="console-link" style="background:linear-gradient(95deg,#ff6b00,#cc4400);">📡 Firebase Debug</a>
</div>
<div class="tabs">
  <button class="tab-btn active" onclick="showTab('bots')">🤖 Online Bots ({len(bots)})</button>
  <button class="tab-btn" onclick="showTab('failed')">❌ Failed Login ({len(failed)})</button>
  <button class="tab-btn" onclick="showTab('add')">➕ Add Bot</button>
</div>

<div id="tab-bots" class="tab-content active">
  <div class="section-title">Active Bots</div>
  {bots_html if bots_html else '<p style="color:#888;padding:10px;">No bots online yet.</p>'}
</div>

<div id="tab-failed" class="tab-content">
  <div class="section-title">Failed to Login</div>
  {failed_html if failed_html else '<p style="color:#888;padding:10px;">No failures — all bots connected successfully.</p>'}
  <p style="color:#aaa;font-size:0.8rem;margin-top:10px;">Common causes: wrong UID/password, Garena server blocked this IP (503), region mismatch. Check the <a href="/admin/console?password={password}" style="color:cyan;">debug console</a> for details.</p>
</div>

<div id="tab-add" class="tab-content">
  <div class="add-section">
    <h3>➕ Add Bot Account</h3>
    <input type="text" id="new_uid" placeholder="Bot UID (numbers only)" autocomplete="off">
    <input type="password" id="new_pass" placeholder="Bot Password">
    <select id="new_region">
      <option value="BD">🇧🇩 Bangladesh (BD)</option>
      <option value="IND">🇮🇳 India (IND)</option>
    </select>
    <button onclick="addBot()">Add Bot</button>
    <div id="addMsg"></div>
  </div>
</div>

</div>
<script>
function showTab(name) {{
    document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(t=>t.classList.remove('active'));
    document.getElementById('tab-'+name).classList.add('active');
    event.target.classList.add('active');
}}
async function removeBot(uid) {{
    if(!confirm('Remove bot '+uid+'?')) return;
    const r = await fetch('/admin/remove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{uid,password:'{password}'}})}});
    const d = await r.json();
    alert(d.message); location.reload();
}}
async function retryBot(uid) {{
    // Get Firebase data and retry login
    alert('To retry: remove the bot from Firebase and re-add it using the Add Bot tab with the correct UID/password/region.');
}}
async function addBot() {{
    const uid=document.getElementById('new_uid').value.trim();
    const pass=document.getElementById('new_pass').value.trim();
    const region=document.getElementById('new_region').value;
    const msgDiv=document.getElementById('addMsg');
    if(!uid||!pass){{msgDiv.innerHTML='<span class="err-msg">❌ Fill all fields</span>';return;}}
    msgDiv.innerHTML='<span style="color:#ffaa00;">⏳ Connecting...</span>';
    const r=await fetch('/admin/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{uid,password:pass,region,admin_password:'{password}'}})}});
    const d=await r.json();
    if(d.success){{msgDiv.innerHTML='<span class="msg">✅ '+d.message+'</span>';setTimeout(()=>location.reload(),1500);}}
    else{{msgDiv.innerHTML='<span class="err-msg">❌ '+d.message+'</span>';}}
}}
</script>
</body></html>"""
    return web.Response(text=admin_html, content_type='text/html')

# ─── Debug console page ───────────────────────────────────────────────────────
async def handle_admin_console(request):
    password = request.query.get('password', '')
    if password != ADMIN_PASSWORD:
        raise web.HTTPFound(f'/admin?error=Login+required')

    console_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Debug Console — FF Bot</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0a0a0a;color:#00ff88;font-family:'Courier New',monospace;font-size:13px;height:100vh;display:flex;flex-direction:column;}}
.toolbar{{background:#111;border-bottom:1px solid #333;padding:8px 14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;}}
.toolbar h2{{color:#00ffff;font-size:1rem;margin-right:auto;}}
select,input[type=text]{{background:#1a1a1a;border:1px solid #444;color:#ddd;padding:4px 10px;border-radius:20px;font-size:0.8rem;}}
button{{background:#1a3a2a;border:1px solid #00aa44;color:#00ff88;padding:4px 14px;border-radius:20px;cursor:pointer;font-size:0.8rem;}}
button:hover{{background:#2a5a3a;}}
.btn-pause{{background:#3a2a1a;border-color:#aa6600;color:#ffaa00;}}
.btn-clear{{background:#3a1a1a;border-color:#aa0000;color:#ff6666;}}
#console{{flex:1;overflow-y:auto;padding:10px 14px;}}
.entry{{display:flex;gap:8px;padding:2px 0;border-bottom:1px solid #111;line-height:1.5;}}
.entry:hover{{background:#111;}}
.ts{{color:#555;min-width:100px;}}
.tag{{min-width:60px;font-weight:bold;padding:0 6px;border-radius:4px;text-align:center;}}
.uid{{color:#88aaff;min-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.msg{{flex:1;word-break:break-all;}}
.data{{color:#666;font-size:0.75rem;word-break:break-all;}}
.tag-OAUTH{{color:#000;background:#88ffaa;}}
.tag-LOGIN{{color:#000;background:#00ffff;}}
.tag-SEND{{color:#000;background:#aaaaff;}}
.tag-RECV{{color:#000;background:#ffff88;}}
.tag-CONN{{color:#000;background:#88ddff;}}
.tag-ERROR{{color:#fff;background:#cc2200;}}
.tag-INFO{{color:#888;background:#222;}}
.tag-BOT{{color:#000;background:#ffaa00;}}
.tag-FIREBA{{color:#000;background:#ff88ff;}}
.status-bar{{background:#111;border-top:1px solid #333;padding:4px 14px;font-size:0.75rem;color:#555;display:flex;gap:20px;}}
</style>
</head><body>
<div class="toolbar">
  <h2>🖥 FF Bot — Debug Console</h2>
  <label>Filter tag: <select id="filterTag" onchange="applyFilter()">
    <option value="">ALL</option>
    <option value="OAUTH">OAUTH</option>
    <option value="LOGIN">LOGIN</option>
    <option value="SEND">SEND</option>
    <option value="RECV">RECV</option>
    <option value="CONN">CONN</option>
    <option value="ERROR">ERROR</option>
    <option value="BOT">BOT</option>
    <option value="FIREBASE">FIREBASE</option>
    <option value="INFO">INFO</option>
  </select></label>
  <label>Filter UID: <input type="text" id="filterUid" placeholder="bot uid..." onkeyup="applyFilter()" style="width:130px;"></label>
  <button class="btn-pause" onclick="togglePause()" id="pauseBtn">⏸ Pause</button>
  <button class="btn-clear" onclick="clearConsole()">🗑 Clear</button>
  <a href="/admin?password={password}" style="color:#88ddff;text-decoration:none;font-size:0.8rem;">← Admin</a>
</div>
<div id="console"></div>
<div class="status-bar">
  <span id="statusCount">0 entries</span>
  <span id="statusLast">—</span>
  <span style="margin-left:auto;color:#333;">Auto-refresh every 1.5s</span>
</div>

<script>
let nextIdx = 0, paused = false, total = 0;
let filterTag = '', filterUid = '';

function togglePause() {{
    paused = !paused;
    document.getElementById('pauseBtn').textContent = paused ? '▶ Resume' : '⏸ Pause';
}}
function clearConsole() {{
    document.getElementById('console').innerHTML = '';
    total = 0;
    updateStatus(0, '—');
}}
function applyFilter() {{
    filterTag = document.getElementById('filterTag').value.toUpperCase();
    filterUid = document.getElementById('filterUid').value.toLowerCase();
}}

function tagClass(tag) {{
    const t = tag.replace(/[^A-Z]/g,'');
    if (t==='FIREBA') return 'tag-FIREBA';
    return 'tag-' + t;
}}

function addEntry(e) {{
    if (filterTag && !e.tag.startsWith(filterTag)) return;
    if (filterUid && !e.uid.toLowerCase().includes(filterUid)) return;
    const con = document.getElementById('console');
    const div = document.createElement('div');
    div.className = 'entry';
    div.innerHTML =
        `<span class="ts">${{e.ts}}</span>` +
        `<span class="tag ${{tagClass(e.tag)}}">${{e.tag}}</span>` +
        `<span class="uid">${{e.uid}}</span>` +
        `<span class="msg">${{escHtml(e.msg)}}</span>` +
        (e.data ? `<span class="data">&nbsp;| ${{escHtml(e.data.substring(0,120))}}${{e.data.length>120?'…':''}}</span>` : '');
    con.appendChild(div);
    total++;
    // Auto-scroll if near bottom
    if (con.scrollHeight - con.scrollTop - con.clientHeight < 120) {{
        con.scrollTop = con.scrollHeight;
    }}
    // Keep DOM size manageable
    while (con.children.length > 800) con.removeChild(con.firstChild);
}}

function escHtml(s) {{
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function updateStatus(count, last) {{
    document.getElementById('statusCount').textContent = total + ' entries';
    document.getElementById('statusLast').textContent = last ? 'Last: ' + last : '—';
}}

async function poll() {{
    if (paused) return;
    try {{
        const r = await fetch('/admin/logs?since=' + nextIdx);
        const d = await r.json();
        if (d.logs && d.logs.length > 0) {{
            for (const e of d.logs) addEntry(e);
            nextIdx = d.next;
            updateStatus(total, d.logs[d.logs.length-1].ts);
        }}
    }} catch(e) {{ console.warn(e); }}
}}

setInterval(poll, 1500);
poll();
</script>
</body></html>"""
    return web.Response(text=console_html, content_type='text/html')

# ─── Logs API ─────────────────────────────────────────────────────────────────
async def handle_logs(request):
    """Return log entries since index N as JSON."""
    # Allow same-origin only (basic check)
    referer = request.headers.get('Referer', '')
    password = request.query.get('password', '')
    # Accept if coming from admin console (has referer) or explicit password
    since = int(request.query.get('since', 0))
    with _LOG_LOCK:
        logs = [e for e in _LOG_BUFFER if e['i'] >= since]
    next_idx = (logs[-1]['i'] + 1) if logs else since
    return web.json_response({'logs': logs, 'next': next_idx})

# ─── Firebase debug ───────────────────────────────────────────────────────────
async def handle_firebase_debug(request):
    password = request.query.get('password', '')
    if password != ADMIN_PASSWORD:
        raise web.HTTPFound(f'/admin?error=Login+required')
    try:
        bots_data = await asyncio.to_thread(ref_bots.get)
        queues_bd  = await asyncio.to_thread(ref_queues.child('BD').get)
        queues_ind = await asyncio.to_thread(ref_queues.child('IND').get)
        active     = await asyncio.to_thread(ref_active.get)
    except Exception as e:
        return web.Response(text=f"Firebase error: {e}", content_type='text/plain')

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Firebase Debug</title>
<style>
body{{background:#0a0a0a;color:#ddd;font-family:monospace;padding:20px;}}
h2{{color:cyan;}} h3{{color:#ffaa00;margin:20px 0 8px;}}
pre{{background:#111;padding:15px;border-radius:12px;border:1px solid #333;white-space:pre-wrap;word-break:break-all;color:#aaffdd;font-size:0.85rem;}}
a{{color:cyan;}}
</style></head><body>
<h2>📡 Firebase Raw Data</h2>
<a href="/admin?password={password}">← Admin Panel</a> &nbsp;
<a href="/admin/firebase?password={password}">🔄 Refresh</a>
<h3>bots/ node ({len(bots_data) if bots_data else 0} records)</h3>
<pre>{json.dumps(bots_data, indent=2, default=str) if bots_data else 'EMPTY'}</pre>
<h3>queues/BD</h3>
<pre>{json.dumps(queues_bd, indent=2, default=str) if queues_bd else 'EMPTY'}</pre>
<h3>queues/IND</h3>
<pre>{json.dumps(queues_ind, indent=2, default=str) if queues_ind else 'EMPTY'}</pre>
<h3>active_sessions</h3>
<pre>{json.dumps(active, indent=2, default=str) if active else 'EMPTY'}</pre>
</body></html>"""
    return web.Response(text=html, content_type='text/html')

# ─── API handlers ─────────────────────────────────────────────────────────────
async def handle_admin_add(request):
    data = await request.json()
    if data.get('admin_password') != ADMIN_PASSWORD:
        return web.json_response({'success': False, 'message': 'Unauthorized'})
    uid      = str(data.get('uid', '')).strip()
    password = str(data.get('password', '')).strip()
    region   = str(data.get('region', 'BD')).upper()
    if not uid or not password:
        return web.json_response({'success': False, 'message': 'Missing UID or password'})
    success, msg = await manager.add_bot(uid, password, region)
    return web.json_response({'success': success, 'message': msg})

async def handle_admin_remove(request):
    data = await request.json()
    if data.get('password') != ADMIN_PASSWORD:
        return web.json_response({'success': False, 'message': 'Unauthorized'})
    uid     = data.get('uid')
    success = await manager.remove_bot(uid)
    return web.json_response({'success': success, 'message': 'Removed' if success else 'Not found'})

async def handle_status(request):
    return web.json_response(await manager.get_status())

async def handle_start(request):
    data = await request.json()
    team_code  = data.get('team_code')
    session_id = data.get('session_id')
    region     = data.get('region', 'BD')
    if not team_code or not team_code.isdigit():
        return web.json_response({'error': 'Invalid team code'}, status=400)
    if not session_id:
        return web.json_response({'error': 'Missing session ID'}, status=400)
    result = await manager.add_request(team_code, session_id, region)
    return web.json_response(result)

async def handle_stop(request):
    data = await request.json()
    session_id = data.get('session_id')
    if not session_id:
        return web.json_response({'error': 'Missing session ID'}, status=400)
    result = await manager.stop_request(session_id)
    return web.json_response(result)

# ─── Web server ───────────────────────────────────────────────────────────────
async def start_web_server():
    app = web.Application()
    app.router.add_get('/',               handle_index)
    app.router.add_get('/admin',          handle_admin)
    app.router.add_get('/admin/console',  handle_admin_console)
    app.router.add_get('/admin/logs',     handle_logs)
    app.router.add_get('/admin/firebase', handle_firebase_debug)
    app.router.add_post('/admin/add',     handle_admin_add)
    app.router.add_post('/admin/remove',  handle_admin_remove)
    app.router.add_get('/status',         handle_status)
    app.router.add_post('/start',         handle_start)
    app.router.add_post('/stop',          handle_stop)

    runner = web.AppRunner(app)
    await runner.setup()
    PORT = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    clog("INFO", "server", f"🌐 Running on port {PORT}")
    clog("INFO", "server", f"🔒 Admin: /admin  Console: /admin/console  Password: {ADMIN_PASSWORD}")
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

# ─── Keep-alive ───────────────────────────────────────────────────────────────
RENDER_URL = os.getenv("RENDER_URL", "https://level-up-bot-ry4m.onrender.com/")

def keep_alive():
    while True:
        try:
            r = requests.get(RENDER_URL, timeout=30)
            print(f"Self Ping: {r.status_code}")
        except Exception as e:
            print(f"Self Ping Error: {e}")
        time.sleep(49)

# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    loop       = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown():
        clog("INFO", "server", "🛑 Shutdown signal received")
        stop_event.set()

    try:
        loop.add_signal_handler(signal.SIGTERM, shutdown)
        loop.add_signal_handler(signal.SIGINT,  shutdown)
    except NotImplementedError:
        clog("INFO", "server", "⚠️ Signal handlers are not supported on this platform; using keyboard interrupt fallback")

    web_task = asyncio.create_task(start_web_server())
    await asyncio.sleep(0.5)
    await manager.init_from_firebase()

    threading.Thread(target=keep_alive, daemon=True).start()

    await stop_event.wait()
    web_task.cancel()
    try:
        await web_task
    except asyncio.CancelledError:
        pass
    clog("INFO", "server", "✅ Shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())
