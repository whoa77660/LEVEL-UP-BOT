# ⚡ FF AUTO LEVEL UP BOT – RNR TEAM ⚡
# Firebase + .env + Graceful shutdown + Keep-alive

import os
import json
import asyncio
import signal
import time
import ssl
import urllib3
import threading
import requests

from datetime import datetime

import aiohttp
from aiohttp import web
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, db

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Your custom modules
from xDL import *
from autoup import AuToUpDaTE
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2
import google.protobuf.json_format as json_format

# ---------- Load .env ----------
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rnr6677")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_KEY_JSON = os.getenv("FIREBASE_KEY_JSON")

if not FIREBASE_KEY_JSON:
    raise RuntimeError("Missing FIREBASE_KEY_JSON environment variable")

# ---------- Firebase init ----------
cred = credentials.Certificate(json.loads(FIREBASE_KEY_JSON))
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DATABASE_URL
})

ref_root = db.reference('/')
ref_bots = ref_root.child('bots')
ref_queues = ref_root.child('queues')
ref_active = ref_root.child('active_sessions')

# ---------- Configuration ----------
START_SPAM_DURATION = 18
WAIT_AFTER_MATCH = 15
LOADING_EXTRA = 5
START_SPAM_DELAY = 0.1
MATCH_DETECT_TIMEOUT = 60
MATCH_DETECT_MIN_SIZE = 50

PACKET_TYPE_BD = "0519"
PACKET_TYPE_IND = "0515"
PACKET_TYPE_DEFAULT = "0515"

# ---------- Helper Functions ----------
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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def SEndPacKeT(ChaT, OnLinE, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        ChaT.write(PacKeT)
        await ChaT.drain()
    elif TypE == 'OnLine' and OnLinE:
        OnLinE.write(PacKeT)
        await OnLinE.drain()

async def GeNeRaTeAccEss(uid, password):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    headers = {
        "Host": "ffmconnect.live.gop.garenanow.com",
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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("open_id"), data.get("access_token")
            return None, None

# ---------- Fetch version + region-specific login URLs ----------
BD_LOGIN_URL, IND_LOGIN_URL, ob, version = AuToUpDaTE()
_bd_src  = "(env override)" if os.environ.get("BD_LOGIN_URL")  else "(auto)"
_ind_src = "(env override)" if os.environ.get("IND_LOGIN_URL") else "(auto)"
print(f"🌐 BD Login URL : {BD_LOGIN_URL}  {_bd_src}")
print(f"🌐 IND Login URL: {IND_LOGIN_URL}  {_ind_src}")
print("💡 Set BD_LOGIN_URL / IND_LOGIN_URL env vars to override these.")
print(f"📦 Version: {version}  OB: {ob}")

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
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = version
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

# --- FIX: accept region-specific login_url as parameter ---
async def MajorLogin(payload, login_url):
    url = f"{login_url}MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
                if response.status == 200:
                    return await response.read()
                print(f"[MajorLogin] HTTP {response.status} from {url}")
                return None
    except Exception as e:
        print(f"[MajorLogin] Connection error to {url}: {e}")
        return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
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
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9:
        headers = '0000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 7:
        headers = '000000000'
    else:
        headers = '0000000'
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
    if region.lower() == "bd":
        packet_type = PACKET_TYPE_BD
    elif region.lower() == "ind":
        packet_type = PACKET_TYPE_IND
    else:
        packet_type = PACKET_TYPE_DEFAULT
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, key, iv)

async def start_auto_packet(key, iv, region):
    fields = {1: 9, 2: {1: 12480598706}}
    if region.lower() == "bd":
        packet_type = PACKET_TYPE_BD
    elif region.lower() == "ind":
        packet_type = PACKET_TYPE_IND
    else:
        packet_type = PACKET_TYPE_DEFAULT
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, key, iv)

async def leave_squad_packet(key, iv, region):
    fields = {1: 7, 2: {1: 12480598706}}
    if region.lower() == "bd":
        packet_type = PACKET_TYPE_BD
    elif region.lower() == "ind":
        packet_type = PACKET_TYPE_IND
    else:
        packet_type = PACKET_TYPE_DEFAULT
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, key, iv)

# ---------- Bot auto loop ----------
async def bot_auto_start_loop(team_code, online_writer, whisper_writer, key, iv, region, stop_event, bot_instance, match_started_event):
    while not stop_event.is_set():
        try:
            join_pkt = await join_teamcode_packet(team_code, key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
            await asyncio.sleep(2)

            match_started_event.clear()
            start_pkt = await start_auto_packet(key, iv, region)
            spam_end = time.time() + START_SPAM_DURATION
            while time.time() < spam_end and not stop_event.is_set() and not match_started_event.is_set():
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', start_pkt)
                await asyncio.sleep(START_SPAM_DELAY)

            if stop_event.is_set():
                break

            start_wait = time.time()
            while not stop_event.is_set():
                if match_started_event.is_set():
                    break
                if time.time() - start_wait >= MATCH_DETECT_TIMEOUT:
                    print(f"[Bot {bot_instance.uid}] No match within {MATCH_DETECT_TIMEOUT}s → freeing bot")
                    leave_pkt = await leave_squad_packet(key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_pkt)
                    await asyncio.sleep(2)
                    return
                await asyncio.sleep(1)

            if stop_event.is_set():
                break

            print(f"[Bot {bot_instance.uid}] Match started – waiting {WAIT_AFTER_MATCH + LOADING_EXTRA}s")
            await asyncio.sleep(WAIT_AFTER_MATCH + LOADING_EXTRA)

            if stop_event.is_set():
                break

            leave_pkt = await leave_squad_packet(key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_pkt)
            await asyncio.sleep(2)
            print(f"[Bot {bot_instance.uid}] Cycle completed for team {team_code}")

        except Exception as e:
            print(f"[Bot {bot_instance.uid}] Error: {e}")
            return

# ---------- BotInstance ----------
class BotInstance:
    def __init__(self, uid, password, region):
        self.uid = uid
        self.password = password
        self.region = region
        # FIX: use region-specific login URL
        if region.upper() == "BD":
            self.login_url = BD_LOGIN_URL
        else:
            self.login_url = IND_LOGIN_URL
        self.online_writer = None
        self.whisper_writer = None
        self.key = None
        self.iv = None
        self.stop_event = None
        self.match_started_event = None
        self.online_task = None
        self.chat_task = None
        self.ready = False
        self.current_job_task = None
        self.current_team = None
        self.is_busy = False
        self.current_session_id = None

    async def login_and_connect(self):
        open_id, access_token = await GeNeRaTeAccEss(self.uid, self.password)
        if not open_id:
            print(f"[Bot {self.uid}] OAuth failed – check credentials")
            return False
        payload = await EncRypTMajoRLoGin(open_id, access_token)
        # FIX: pass self.login_url so each bot hits the correct regional server
        login_resp = await MajorLogin(payload, self.login_url)
        if not login_resp:
            print(f"[Bot {self.uid}] MajorLogin failed – URL: {self.login_url}")
            return False
        auth = await DecRypTMajoRLoGin(login_resp)
        token = auth.token
        if not token:
            print(f"[Bot {self.uid}] No token in MajorLogin response")
            return False
        url = auth.url
        self.key = auth.key
        self.iv = auth.iv
        timestamp = auth.timestamp
        login_data = await GetLoginData(url, payload, token)
        if not login_data:
            print(f"[Bot {self.uid}] GetLoginData failed")
            return False
        ports = await DecRypTLoGinDaTa(login_data)
        online_ip, online_port = ports.Online_IP_Port.split(":")
        chat_ip, chat_port = ports.AccountIP_Port.split(":")
        auth_token = await xAuThSTarTuP(int(auth.account_uid), token, int(timestamp), self.key, self.iv)

        self.stop_event = asyncio.Event()
        self.match_started_event = asyncio.Event()

        async def online_loop():
            while not self.stop_event.is_set():
                try:
                    reader, writer = await asyncio.open_connection(online_ip, int(online_port))
                    self.online_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    while not self.stop_event.is_set():
                        data = await reader.read(9999)
                        if not data:
                            break
                        if len(data) > MATCH_DETECT_MIN_SIZE:
                            self.match_started_event.set()
                    writer.close()
                    await writer.wait_closed()
                    self.online_writer = None
                    break
                except Exception as e:
                    print(f"[Bot {self.uid}] online error: {e}")
                    await asyncio.sleep(5)

        async def chat_loop():
            while not self.stop_event.is_set():
                try:
                    reader, writer = await asyncio.open_connection(chat_ip, int(chat_port))
                    self.whisper_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    if hasattr(ports, 'Clan_ID') and ports.Clan_ID:
                        clan_pkt = await AuthClan(ports.Clan_ID, ports.Clan_Compiled_Data, self.key, self.iv)
                        writer.write(clan_pkt)
                        await writer.drain()
                    while not self.stop_event.is_set():
                        await asyncio.sleep(1)
                    writer.close()
                    await writer.wait_closed()
                    self.whisper_writer = None
                    break
                except Exception as e:
                    print(f"[Bot {self.uid}] chat error: {e}")
                    await asyncio.sleep(5)

        if self.online_task:
            self.online_task.cancel()
        if self.chat_task:
            self.chat_task.cancel()
        self.online_task = asyncio.create_task(online_loop())
        self.chat_task = asyncio.create_task(chat_loop())
        await asyncio.sleep(3)
        self.ready = True
        return True

    async def reconnect(self):
        print(f"[Bot {self.uid}] Reconnecting...")
        self.ready = False
        if self.stop_event:
            self.stop_event.set()
        if self.current_job_task and not self.current_job_task.done():
            self.current_job_task.cancel()
        self.is_busy = False
        self.current_team = None
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
            print(f"[Bot {self.uid}] Reconnect FAILED.")
            self.ready = False
        else:
            print(f"[Bot {self.uid}] Reconnect successful.")
            self.ready = True

    async def start_job(self, team_code, manager, session_id):
        if not self.ready or self.is_busy:
            return
        self.is_busy = True
        self.current_team = team_code
        self.current_session_id = session_id
        self.stop_event.clear()
        self.match_started_event.clear()
        self.current_job_task = asyncio.create_task(
            bot_auto_start_loop(team_code, self.online_writer, self.whisper_writer,
                                self.key, self.iv, self.region, self.stop_event,
                                self, self.match_started_event)
        )
        try:
            await self.current_job_task
        except asyncio.CancelledError:
            pass
        self.is_busy = False
        self.current_team = None
        self.current_session_id = None
        await manager.bot_finished(self)

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

# ---------- QueueManager ----------
class QueueManager:
    def __init__(self):
        self.bots = []
        self.bot_dict = {}

    async def init_from_firebase(self):
        bots_data = await asyncio.to_thread(ref_bots.get)
        if not bots_data:
            print("No bots found in Firebase.")
            return
        for uid, data in bots_data.items():
            bot = BotInstance(uid, data['password'], data['region'])
            print(f"🔐 Logging in bot {uid} (region {data['region']}, url {bot.login_url})...")
            success = await bot.login_and_connect()
            if success:
                self.bots.append(bot)
                self.bot_dict[uid] = bot
                await asyncio.to_thread(ref_bots.child(uid).update, {'ready': True})
                print(f"✅ Bot {uid} ready")
            else:
                print(f"❌ Bot {uid} login failed")
        print(f"🎉 Bot loading complete. Total {len(self.bots)} bots online.")

    async def add_bot(self, uid, password, region):
        bot = BotInstance(uid, password, region)
        if await bot.login_and_connect():
            self.bots.append(bot)
            self.bot_dict[uid] = bot
            await asyncio.to_thread(ref_bots.child(uid).set, {
                'password': password,
                'region': region,
                'ready': True,
                'busy': False,
                'current_team': None,
                'current_session_id': None
            })
            return True, "Bot added and connected"
        else:
            return False, "Login failed"

    async def remove_bot(self, uid):
        bot = self.bot_dict.get(uid)
        if bot:
            await bot.disconnect()
            self.bots.remove(bot)
            del self.bot_dict[uid]
            await asyncio.to_thread(ref_bots.child(uid).delete)
            return True
        return False

    async def add_request(self, team_code, session_id, region):
        active_data = await asyncio.to_thread(ref_active.child(session_id).get)
        if active_data:
            return {'status': 'error', 'message': 'You already have a bot running. Stop it first.'}

        for bot in self.bots:
            if bot.ready and not bot.is_busy and bot.region == region:
                await asyncio.to_thread(ref_active.child(session_id).set, {
                    'bot_uid': bot.uid,
                    'region': region,
                    'team_code': team_code,
                    'started_at': datetime.now().isoformat()
                })
                asyncio.create_task(bot.start_job(team_code, self, session_id))
                return {'status': 'started', 'bot_uid': bot.uid, 'queue_position': 0}

        queue_ref = ref_queues.child(region)
        new_entry = {'team_code': team_code, 'session_id': session_id}
        await asyncio.to_thread(queue_ref.push, new_entry)
        queue_snapshot = await asyncio.to_thread(queue_ref.get)
        position = len(queue_snapshot) if queue_snapshot else 1
        return {'status': 'queued', 'queue_position': position}

    async def stop_request(self, session_id):
        active_data = await asyncio.to_thread(ref_active.child(session_id).get)
        if active_data:
            bot_uid = active_data['bot_uid']
            bot = self.bot_dict.get(bot_uid)
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

        region = bot.region
        queue_ref = ref_queues.child(region)
        q_snapshot = await asyncio.to_thread(queue_ref.get)
        if q_snapshot:
            first_key = next(iter(q_snapshot))
            entry = q_snapshot[first_key]
            team_code = entry['team_code']
            session_id = entry['session_id']
            for b in self.bots:
                if b.ready and not b.is_busy and b.region == region:
                    await asyncio.to_thread(ref_active.child(session_id).set, {
                        'bot_uid': b.uid,
                        'region': region,
                        'team_code': team_code,
                        'started_at': datetime.now().isoformat()
                    })
                    asyncio.create_task(b.start_job(team_code, self, session_id))
                    await asyncio.to_thread(queue_ref.child(first_key).delete)
                    break

    async def get_status(self):
        bots_status = []
        for bot in self.bots:
            bots_status.append({
                'uid': bot.uid,
                'region': bot.region,
                'busy': bot.is_busy,
                'current_team': bot.current_team if bot.is_busy else None,
                'ready': bot.ready
            })
        bd_queue = await asyncio.to_thread(ref_queues.child('BD').get) or {}
        ind_queue = await asyncio.to_thread(ref_queues.child('IND').get) or {}
        queue_info = {
            'BD': [{'team_code': v['team_code'], 'session_id': v['session_id'][:8]} for v in bd_queue.values()],
            'IND': [{'team_code': v['team_code'], 'session_id': v['session_id'][:8]} for v in ind_queue.values()]
        }
        return {'bots': bots_status, 'queues': queue_info}

    def get_bots_list(self):
        return [{'uid': b.uid, 'region': b.region, 'ready': b.ready} for b in self.bots]

# ---------- Global manager ----------
manager = QueueManager()

# ---------- Web Handlers ----------
async def handle_index(request):
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>FF AUTO LEVEL UP BOT | RNR TEAM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', system-ui, 'Segoe UI', Roboto, sans-serif; }
        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #0a0f1e 0%, #0a1a2a 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
        }
        .glass-card {
            background: rgba(15, 25, 45, 0.85);
            backdrop-filter: blur(12px);
            border-radius: 2rem;
            border: 1px solid rgba(0, 255, 255, 0.4);
            box-shadow: 0 25px 45px rgba(0,0,0,0.3), 0 0 20px rgba(0,255,255,0.2);
            padding: 2rem;
            width: 100%;
            max-width: 800px;
            transition: all 0.3s ease;
            z-index: 2;
        }
        h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-align: center;
            margin-bottom: 0.25rem;
            letter-spacing: -0.5px;
        }
        .credit {
            text-align: center;
            font-size: 0.8rem;
            color: #88aaff;
            margin-bottom: 0.5rem;
        }
        .credit a {
            color: cyan;
            text-decoration: none;
        }
        .sub {
            text-align: center;
            color: #b8e2ff;
            margin-bottom: 1.5rem;
            font-size: 0.8rem;
            border-bottom: 1px dashed rgba(100,200,255,0.5);
            display: inline-block;
            width: auto;
            padding-bottom: 5px;
        }
        .region-toggle {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 25px;
        }
        .region-btn {
            background: rgba(0,0,0,0.5);
            border: 2px solid #00aaff;
            border-radius: 60px;
            padding: 10px 30px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            color: white;
        }
        .region-btn.active {
            background: linear-gradient(95deg, #00b4db, #0083b0);
            border-color: white;
            box-shadow: 0 0 12px cyan;
        }
        .input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .input-group input {
            flex: 2;
            min-width: 180px;
            background: rgba(0,0,0,0.6);
            border: 1px solid #00aaff;
            border-radius: 60px;
            padding: 14px 20px;
            font-size: 1rem;
            color: #ffffff;
            outline: none;
            transition: 0.2s;
        }
        .input-group input:focus {
            border-color: #00ffff;
            box-shadow: 0 0 10px rgba(0,255,255,0.5);
            background: rgba(0,0,0,0.8);
        }
        button {
            background: linear-gradient(95deg, #00b4db, #0083b0);
            border: none;
            border-radius: 60px;
            padding: 12px 28px;
            font-weight: bold;
            font-size: 1rem;
            color: white;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,180,255,0.4); }
        .stop-btn { background: linear-gradient(95deg, #d64545, #b12a2a); }
        .status-panel {
            background: rgba(0,0,0,0.5);
            border-radius: 1.5rem;
            padding: 1.2rem;
            margin: 25px 0;
            border: 1px solid rgba(0,255,255,0.3);
        }
        .status-panel h3 { color: #ffffff; margin-bottom: 12px; font-weight: 600; letter-spacing: 1px; }
        .bot-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            gap: 10px;
            flex-wrap: wrap;
        }
        .bot-uid { font-family: monospace; font-weight: 700; background: #0a2a3a; padding: 4px 12px; border-radius: 40px; font-size: 0.9rem; color: white; border: 1px solid #00aaff; flex: 1; }
        .bot-region { background: #1e3a5f; padding: 4px 12px; border-radius: 40px; font-size: 0.8rem; font-weight: bold; color: cyan; min-width: 50px; text-align: center; }
        .status-badge { padding: 5px 14px; border-radius: 40px; font-size: 0.8rem; font-weight: bold; min-width: 110px; text-align: center; }
        .free { background: #1e7e34; color: white; box-shadow: 0 0 5px #00ff88; }
        .busy { background: #c0392b; color: white; box-shadow: 0 0 5px #ff4444; }
        .reconnecting { background: #f0ad4e; color: black; box-shadow: 0 0 5px #ffaa00; }
        .queue-section { margin-top: 15px; }
        .queue-title { font-size: 0.9rem; font-weight: bold; color: cyan; margin: 10px 0 5px; }
        .queue-list { max-height: 150px; overflow-y: auto; }
        .queue-item { background: rgba(0,20,40,0.7); margin: 4px 0; padding: 6px 12px; border-radius: 30px; font-size: 0.8rem; display: flex; justify-content: space-between; color: #e0e0e0; border: 1px solid rgba(0,200,255,0.3); }
        footer { text-align: center; margin-top: 25px; font-size: 0.75rem; color: #aaccee; }
        .admin-link { color: #88ddff; text-decoration: none; font-weight: 600; }
        .telegram-icon {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 52px;
            height: 52px;
            background: #0088cc;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: transform 0.2s;
            z-index: 100;
            cursor: pointer;
        }
        .telegram-icon:hover { transform: scale(1.1); }
        .telegram-icon svg { width: 30px; height: 30px; fill: white; }
        .toast {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(8px);
            color: white;
            padding: 12px 24px;
            border-radius: 60px;
            font-size: 0.9rem;
            font-weight: bold;
            z-index: 1000;
            transition: opacity 0.3s;
            pointer-events: none;
            border-left: 5px solid cyan;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .rules-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            backdrop-filter: blur(5px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .rules-card {
            background: rgba(15,25,45,0.95);
            border-radius: 2rem;
            padding: 2rem;
            max-width: 550px;
            width: 90%;
            border: 1px solid cyan;
            color: white;
            text-align: center;
        }
        .rules-card h2 { color: cyan; margin-bottom: 1rem; }
        .rules-card h3 { color: #aaaaff; margin: 1rem 0 0.5rem; font-size: 1rem; }
        .rules-card p { margin: 0.5rem 0; line-height: 1.4; }
        .rules-card a { color: cyan; text-decoration: none; }
        .rules-card a:hover { text-decoration: underline; }
        .rules-card button { background: cyan; color: black; margin-top: 1rem; border: none; }
        .loading-status {
            margin-top: 15px;
            padding: 10px;
            background: rgba(0,0,0,0.4);
            border-radius: 60px;
            font-size: 0.8rem;
            color: #aaffdd;
            text-align: center;
        }
        @media (max-width: 550px) { .glass-card { padding: 1.5rem; } .input-group { flex-direction: column; } button { width: 100%; } }
    </style>
</head>
<body>
<div class="glass-card">
    <h1>⚡ FF AUTO LEVEL UP BOT</h1>
    <div class="credit">🚀 RNR TEAM — <a href="https://t.me/Rahmttollah" target="_blank">@Rahmttollah</a></div>
    <div style="text-align:center;"><span class="sub">PREMIUM | JUST PUT YOUR TEAM CODE</span></div>
    <div class="region-toggle">
        <div id="btnBD" class="region-btn active" onclick="setRegion('BD')">🇧🇩 BANGLADESH</div>
        <div id="btnIND" class="region-btn" onclick="setRegion('IND')">🇮🇳 INDIA</div>
    </div>
    <div class="input-group">
        <input type="text" id="teamcode" placeholder="Enter team code (digits only)" inputmode="numeric" autocomplete="off">
        <button id="pasteBtn" type="button" style="background: #2c5a7a;">📋 Paste</button>
        <button id="startBtn">▶ START LEVELING</button>
        <button id="stopBtn" class="stop-btn">⏹ STOP MY BOT</button>
    </div>
    <div class="status-panel">
        <h3>🤖 BOT FLEET STATUS</h3>
        <div id="botsContainer"></div>
        <div class="queue-section">
            <div class="queue-title" id="queueTitle">📋 QUEUE (BANGLADESH)</div>
            <div id="queueList" class="queue-list"></div>
        </div>
        <div id="loadingStatus" class="loading-status"></div>
    </div>
    <footer>
        🔒 Your session is private · <a href="/admin" class="admin-link" target="_blank">Admin Panel</a>
    </footer>
</div>
<a href="https://t.me/Rahmttollah" target="_blank" class="telegram-icon">
    <svg viewBox="0 0 24 24" fill="white">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 14.56c-.2.58-.82.82-1.36.6l-2.4-1.2-2.4 1.2c-.54.22-1.16-.02-1.36-.6-.2-.58.06-1.14.6-1.36l2.4-1.2-2.4-1.2c-.54-.22-.8-.78-.6-1.36.2-.58.82-.82 1.36-.6l2.4 1.2 2.4-1.2c.54-.22 1.16.02 1.36.6.2.58-.06 1.14-.6 1.36l-2.4 1.2 2.4 1.2c.54.22.8.78.6 1.36z"/>
    </svg>
</a>

<div id="rulesModal" class="rules-modal" style="display:none;">
    <div class="rules-card">
        <h2>🚀 FF AUTO LEVEL UP BOT — Rahmttollah</h2>
        <p>━━━━━━━━━━━━━━</p>
        <h3>📌 Use | ব্যবহার | उपयोग</h3>
        <p>🇬🇧 Open Garena Free Fire → Lone Wolf (Dual VS) → Copy Code → Paste → Auto Join & Level Up</p>
        <p>🇧🇩 Free Fire খুলুন → Lone Wolf (Dual VS) → Code কপি → এখানে দিন → বট জয়েন করবে</p>
        <p>🇮🇳 Free Fire खोलें → Lone Wolf (Dual VS) → Code कॉपी → यहाँ पेस्ट → बॉट जॉइन करेगा</p>
        <p>━━━━━━━━━━━━━━</p>
        <h3>⚠️ Rules | নিয়ম | नियम</h3>
        <p>🇬🇧 Valid code • Stay online • No spam/fake • Misuse = Ban</p>
        <p>🇧🇩 সঠিক কোড • অনলাইনে থাকুন • স্প্যাম নয় • অপব্যবহার = ব্যান</p>
        <p>🇮🇳 सही कोड • ऑनलाइन रहें • स्पैम नहीं • गलत उपयोग = बैन</p>
        <p>━━━━━━━━━━━━━━</p>
        <h3>🤖 About | সম্পর্কে | बारे में</h3>
        <p>🇬🇧 Auto joins & boosts leveling</p>
        <p>🇧🇩 অটো জয়েন করে লেভেল বাড়ায়</p>
        <p>🇮🇳 ऑटो जॉइन करके लेवल बढ़ाता है</p>
        <p>━━━━━━━━━━━━━━</p>
        <h3>📢 Creator & Support</h3>
        <p>👤 Rahmttollah (Dev)<br>📺 <a href="https://t.me/RNRCHANNELS" target="_blank">t.me/RNRCHANNELS</a> — Updates<br>🛠️ <a href="https://t.me/Rahmttollah" target="_blank">t.me/Rahmttollah</a> — Help/Report</p>
        <button onclick="closeRules()">GOT IT</button>
    </div>
</div>

<script>
    let sessionId = localStorage.getItem('ff_session');
    if (!sessionId) {
        sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            let r = Math.random()*16|0, v = c==='x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
        localStorage.setItem('ff_session', sessionId);
    }
    if (!localStorage.getItem('rules_seen')) {
        document.getElementById('rulesModal').style.display = 'flex';
        localStorage.setItem('rules_seen', 'true');
    }
    function closeRules() { document.getElementById('rulesModal').style.display = 'none'; }
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        if (type === 'error') toast.style.borderLeftColor = 'red';
        else if (type === 'success') toast.style.borderLeftColor = 'lime';
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }, 3000);
    }
    let currentRegion = 'BD';

    // ---------- Paste button ----------
    document.getElementById('pasteBtn').addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            const input = document.getElementById('teamcode');
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            showToast('📋 Pasted from clipboard', 'success');
        } catch (err) {
            showToast('❌ Failed to paste – clipboard access denied', 'error');
        }
    });

    function setRegion(reg) {
        currentRegion = reg;
        document.getElementById('btnBD').classList.toggle('active', reg === 'BD');
        document.getElementById('btnIND').classList.toggle('active', reg === 'IND');
        document.getElementById('queueTitle').innerText = reg === 'BD' ? '📋 QUEUE (BANGLADESH)' : '📋 QUEUE (INDIA)';
        refreshStatus();
    }
    async function refreshStatus() {
        try {
            const res = await fetch('/status');
            const data = await res.json();
            const botsDiv = document.getElementById('botsContainer');
            botsDiv.innerHTML = '';
            const filteredBots = data.bots.filter(b => b.region === currentRegion);
            for (let b of filteredBots) {
                const div = document.createElement('div');
                div.className = 'bot-item';
                let statusText = '', statusClass = '';
                if (b.busy) { statusText = `BUSY · team ${b.current_team}`; statusClass = 'busy'; }
                else if (!b.ready) { statusText = 'RECONNECTING...'; statusClass = 'reconnecting'; }
                else { statusText = 'FREE'; statusClass = 'free'; }
                div.innerHTML = `<span class="bot-uid">${b.uid}</span><span class="bot-region">${b.region}</span><span class="status-badge ${statusClass}">${statusText}</span>`;
                botsDiv.appendChild(div);
            }
            if (filteredBots.length === 0) botsDiv.innerHTML = '<div class="bot-item">✨ No bots available for this region</div>';
            const queueList = document.getElementById('queueList');
            queueList.innerHTML = '';
            const regionQueue = data.queues[currentRegion];
            for (let q of regionQueue) {
                const item = document.createElement('div');
                item.className = 'queue-item';
                item.innerHTML = `<span>🎮 Team ${q.team_code}</span><span>⏳ ${q.session_id}...</span>`;
                queueList.appendChild(item);
            }
            if (regionQueue.length === 0) queueList.innerHTML = '<div class="queue-item">✨ No waiting requests</div>';
            const loadingDiv = document.getElementById('loadingStatus');
            const onlineBots = data.bots.filter(b => b.ready).length;
            loadingDiv.innerHTML = `✅ ${onlineBots} bots online · ${data.bots.length} total`;
        } catch(e) { console.warn(e); }
    }
    let autoStartEnabled = true;
    const teamcodeInput = document.getElementById('teamcode');
    async function autoStartIfReady() {
        const teamcode = teamcodeInput.value.trim();
        if (autoStartEnabled && teamcode.length === 7 && /^\d+$/.test(teamcode)) {
            autoStartEnabled = false;
            document.getElementById('startBtn').click();
            setTimeout(() => { autoStartEnabled = true; }, 2000);
        }
    }
    teamcodeInput.addEventListener('input', autoStartIfReady);
    teamcodeInput.addEventListener('paste', () => { setTimeout(autoStartIfReady, 10); });
    document.getElementById('startBtn').onclick = async () => {
        const teamcode = teamcodeInput.value.trim();
        if (!teamcode || !/^\d+$/.test(teamcode)) {
            showToast('❌ Enter a valid numeric team code', 'error');
            return;
        }
        const res = await fetch('/start', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({team_code: teamcode, session_id: sessionId, region: currentRegion})
        });
        const data = await res.json();
        if (data.error) showToast(`❌ ${data.error}`, 'error');
        else if (data.queue_position) showToast(`⏳ Queued at position ${data.queue_position} (${currentRegion})`, 'info');
        else showToast(`✅ Started immediately on bot ${data.bot_uid}`, 'success');
        refreshStatus();
    };
    document.getElementById('stopBtn').onclick = async () => {
        const res = await fetch('/stop', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({session_id: sessionId})
        });
        const data = await res.json();
        showToast(data.message || data.error || 'Bot stopped', data.error ? 'error' : 'success');
        refreshStatus();
    };
    setInterval(refreshStatus, 2500);
    refreshStatus();
</script>
</body>
</html>"""
    return web.Response(text=html, content_type='text/html')

# ---------- Admin handler ----------
async def handle_admin(request):
    password = request.query.get('password', '')
    if password != ADMIN_PASSWORD:
        login_html = r"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin Login</title><style>
body{background:#0a0f1e;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;}
.card{background:rgba(0,0,0,0.8);backdrop-filter:blur(10px);padding:2rem;border-radius:2rem;border:1px solid cyan;}
input,button{padding:12px;margin:8px;border-radius:40px;border:none;}
input{background:#111;color:white;border:1px solid cyan;}
button{background:cyan;font-weight:bold;color:black;}
h2{color:white;}
</style></head><body><div class='card'><h2>🔐 Admin Access</h2><form method='get'><input type='password' name='password' placeholder='Admin Password'><button type='submit'>Enter</button></form></div></body></html>"""
        return web.Response(text=login_html, content_type='text/html')

    bots = manager.get_bots_list()
    bots_html = "".join(f"<div class='bot-card'><span style='color:white;font-weight:bold;'>{b['uid']}</span> <span style='color:#88ff88;'>{b['region']}</span> <span style='color:cyan;'>{'✅' if b['ready'] else '⚠️'}</span> <button onclick=\"removeBot('{b['uid']}')\">🗑 Remove</button></div>" for b in bots)

    admin_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Panel - Bot Manager</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif;}}
    body{{background:linear-gradient(145deg,#071a25,#021018);padding:30px;color:#ffffff;}}
    .container{{max-width:800px;margin:auto;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);border-radius:2rem;padding:2rem;border:1px solid cyan;}}
    h1{{text-align:center;margin-bottom:20px;color:cyan;}}
    .bot-card{{background:#0a1a2e;margin:12px 0;padding:12px 18px;border-radius:60px;display:flex;justify-content:space-between;align-items:center;}}
    .bot-card span{{color:white;}}
    button{{background:#2c5a7a;border:none;padding:8px 20px;border-radius:40px;color:white;cursor:pointer;transition:0.2s;}}
    button:hover{{background:#00a8cc;transform:scale(1.02);}}
    .add-section{{margin-top:30px;background:#01121c;padding:20px;border-radius:1.5rem;}}
    input, select{{background:#102b37;border:1px solid cyan;padding:12px;border-radius:40px;color:white;width:calc(50% - 20px);margin:5px;}}
    .logout{{float:right;color:cyan;text-decoration:none;}}
    .add-section h3{{color:#aaffff;margin-bottom:12px;}}
    </style>
</head><body>
<div class="container">
    <h1>👑 ADMIN DASHBOARD <a href="/?password={ADMIN_PASSWORD}" class='logout'>⬅ Back</a></h1>
    <div id="botlist">{bots_html}</div>
    <div class="add-section">
        <h3>➕ Add New Bot Account</h3>
        <input type="text" id="new_uid" placeholder="UID" autocomplete="off">
        <input type="password" id="new_pass" placeholder="Password">
        <select id="new_region">
            <option value="BD">Bangladesh (BD)</option>
            <option value="IND">India (IND)</option>
        </select>
        <button onclick="addBot()">Add Bot</button>
        <div id="addMsg" style="color:#88ff88; margin-top:10px;"></div>
    </div>
</div>
<script>
    async function removeBot(uid) {{
        if(!confirm("Remove bot "+uid+"?")) return;
        let res = await fetch('/admin/remove', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{uid: uid, password: "{ADMIN_PASSWORD}"}})}});
        let data = await res.json();
        alert(data.message);
        location.reload();
    }}
    async function addBot() {{
        let uid = document.getElementById('new_uid').value.trim();
        let pass = document.getElementById('new_pass').value.trim();
        let region = document.getElementById('new_region').value;
        if(!uid || !pass) {{ alert("Fill all fields"); return; }}
        let res = await fetch('/admin/add', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{uid: uid, password: pass, region: region, admin_password: "{ADMIN_PASSWORD}"}})}});
        let data = await res.json();
        if (data.success) {{
            document.getElementById('addMsg').innerText = data.message;
            setTimeout(()=>location.reload(), 1000);
        }} else {{
            document.getElementById('addMsg').innerText = '❌ ' + (data.message || 'Unknown error');
        }}
    }}
</script>
</body></html>"""
    return web.Response(text=admin_html, content_type='text/html')

async def handle_admin_add(request):
    data = await request.json()
    if data.get('admin_password') != ADMIN_PASSWORD:
        return web.json_response({'success': False, 'message': 'Unauthorized'})
    uid = data.get('uid')
    password = data.get('password')
    region = data.get('region', 'BD')
    if not uid or not password:
        return web.json_response({'success': False, 'message': 'Missing fields'})
    success, msg = await manager.add_bot(uid, password, region)
    return web.json_response({'success': success, 'message': msg})

async def handle_admin_remove(request):
    data = await request.json()
    if data.get('password') != ADMIN_PASSWORD:
        return web.json_response({'success': False, 'message': 'Unauthorized'})
    uid = data.get('uid')
    success = await manager.remove_bot(uid)
    return web.json_response({'success': success, 'message': 'Removed' if success else 'Not found'})

async def handle_status(request):
    return web.json_response(await manager.get_status())

async def handle_start(request):
    data = await request.json()
    team_code = data.get('team_code')
    session_id = data.get('session_id')
    region = data.get('region', 'BD')
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

# ---------- Web server ----------
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/admin', handle_admin)
    app.router.add_post('/admin/add', handle_admin_add)
    app.router.add_post('/admin/remove', handle_admin_remove)
    app.router.add_get('/status', handle_status)
    app.router.add_post('/start', handle_start)
    app.router.add_post('/stop', handle_stop)
    runner = web.AppRunner(app)
    await runner.setup()
    PORT = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌐 FF AUTO LEVEL UP BOT – http://localhost:{PORT}")
    print(f"🔒 Admin Panel: http://localhost:{PORT}/admin (password: {ADMIN_PASSWORD})")
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

# ---------- Keep-alive thread ----------
RENDER_URL = os.getenv("RENDER_URL", "https://level-up-bot-0zdm.onrender.com/")

def keep_alive():
    while True:
        try:
            response = requests.get(RENDER_URL, timeout=30)
            print(f"Self Ping: {response.status_code}")
        except Exception as e:
            print(f"Self Ping Error: {e}")
        time.sleep(49)

# ---------- Main ----------
async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown():
        print("🛑 Shutdown signal received, stopping gracefully...")
        stop_event.set()

    loop.add_signal_handler(signal.SIGTERM, shutdown)
    loop.add_signal_handler(signal.SIGINT, shutdown)

    web_task = asyncio.create_task(start_web_server())
    await asyncio.sleep(0.5)
    await manager.init_from_firebase()

    # Start keep-alive thread (daemon)
    threading.Thread(target=keep_alive, daemon=True).start()

    await stop_event.wait()
    web_task.cancel()
    try:
        await web_task
    except asyncio.CancelledError:
        pass
    print("✅ Bot shut down successfully.")

if __name__ == '__main__':
    asyncio.run(main())
