import requests
import urllib3
import logging
from functools import wraps
from colorama import Fore, Back, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ensure_session(f):
    @wraps(f)
    def wrapper(instance, *args, **kwargs):
        # Ensure the session is valid before proceeding
        if not instance.check_login():
            print("Session is invalid or expired. Re-establishing session.")
            instance.login()
        return f(instance, *args, **kwargs)

    return wrapper


class FortiManager:
    def __init__(self, host, username, password, adom="root", verify=False):
        self.host = host
        self.username = username
        self.password = password
        self.adom = adom
        self.sessionid = "null"
        self.verify = verify
        self.session = 'null'
        if not self.verify:
            protocol = "http"
        else:
            protocol = "https"
        protocol = "https"
        self.base_url = f"{protocol}://{self.host}/jsonrpc"

    @ensure_session
    def get_devices(self):
        session = self.session
        payload = {"method": "get", "params": [
            {"url": f"/dvmdb/adom/{self.adom}/device/"}]}
        payload.update({"session": self.sessionid})
        get_devices = session.post(
            url=self.base_url, json=payload, verify=False)
        return get_devices.json()

    @ensure_session
    def getstatus(self, fname):
        session = self.session
        payload = {
            "method": "exec",
            "params": [
                {
                    "data": {
                        "action": "get",
                        "payload": {},
                        "resource": "/api/v2/monitor/system/status/",
                        "target": [f"device/{fname}/"]
                    },
                    "url": "/sys/proxy/json"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        getstatus = session.post(url=self.base_url, json=payload, verify=self.verify)
        return getstatus.json()

    @ensure_session
    def get_adoms(self, name=False):
        url = "dvmdb/adom"
        if name:
            url = f"dvmdb/adom/{name}"
        session = self.session
        payload = \
            {
                "method": "get",
                "params":
                    [
                        {
                            "url": url,
                            "option": "object member"
                        }
                    ],
                "session": self.sessionid
            }
        get_adoms = session.post(url=self.base_url, json=payload, verify=self.verify)
        return get_adoms.json()["result"]

    # Login Method
    def login(self):
        """
        Log in to FortiManager with the details provided during object creation of this class
        :return: Session
        """
        session = requests.session()
        payload = \
            {
                "method": "exec",
                "params":
                    [
                        {
                            "data": {
                                "passwd": self.password,
                                "user": self.username
                            },
                            "url": "/sys/login/user"
                        }
                    ],
                "session": self.sessionid
            }
        payload = repr(payload)
        login = session.post(url=self.base_url, data=payload, verify=self.verify)
        self.sessionid = login.json()['session']
        self.session = session
        return session

    @ensure_session
    def logout(self):
        """
        Logout from FortiManager
        :return: Response of status code with data in JSON Format
        """
        session = self.session
        payload = \
            {
                "method": "exec",
                "params":
                    [
                        {
                            "url": "sys/logout"
                        }
                    ],
                "session": self.sessionid
            }
        payload = repr(payload)
        logout = session.post(url=self.base_url, data=payload, verify=self.verify)
        self.session = 'null'
        return logout.json()["result"]

    @ensure_session
    def add_model_device(self, device_name, serial_num, description, BB1_DESC, BB1_GW,
                         BB1_IP, BB1_MASK, BB2_DESC, BB2_GW, BB2_IP, BB2_MASK,
                         MPLS_GW, MPLS_IP, NETWORK_CORP, NETWORK_LOOPBACK, NETWORK_MISC,
                         NETWORK_STORE, NETWORK_WIRELESS, STORE_NUMBER, STORE_SW01_SN,
                         username="admin", password=""):
        session = self.session
        payload = {
            "method": "exec",
            "params": [
                {
                    "url": "dvm/cmd/add/device",
                    "data": {
                        "adom": self.adom,
                        "flags": [
                            "create_task"
                        ],
                        "device": {
                            "name": device_name,
                            "adm_usr": "admin",
                            "os_ver": 7,
                            "version": 700,
                            "os_type": 0,
                            "mr": 0,
                            "platform_str": "FortiGate-61F",
                            "mgmt_mode": 3,
                            "flags": 67371040,
                            "prefer_img_ver": "7.0.11-b489",
                            "sn": serial_num,
                            "faz.perm": 15,
                            "faz.quota": 0,
                            "platform_id": 21,
                            "branch_pt": 485,
                            "build": 485,
                            "desc": description,
                            "meta fields": {
                                "BB1_DESC": f"{BB1_DESC}",
                                "BB1_GW": f"{BB1_GW}",
                                "BB1_IP": f"{BB1_IP}",
                                "BB1_MASK": f"{BB1_MASK}",
                                "BB2_DESC": f"{BB2_DESC}",
                                "BB2_GW": f"{BB2_GW}",
                                "BB2_IP": f"{BB2_IP}",
                                "BB2_MASK": f"{BB2_MASK}",
                                "MPLS_GW": f"{MPLS_GW}",
                                "MPLS_IP": f"{MPLS_IP}",
                                "NETWORK_CORP": f"{NETWORK_CORP}",
                                "NETWORK_LOOPBACK": f"{NETWORK_LOOPBACK}",
                                "NETWORK_MISC": f"{NETWORK_MISC}",
                                "NETWORK_STORE": f"{NETWORK_STORE}",
                                "NETWORK_WIRELESS": f"{NETWORK_WIRELESS}",
                                "STORE_NUMBER": f"{STORE_NUMBER}",
                                "STORE_SW01_SN": f"{STORE_SW01_SN}"
                            },
                        }
                    }
                }
            ]
        }
        payload.update({"session": self.sessionid})
        add_model_device = session.post(url=self.base_url, json=payload, verify=False)
        return add_model_device.json()["result"]

    @ensure_session
    def assigncli_template(self, device_name, temp_name):
        session = self.session
        payload = {
            "method": "add",
            "params": [
                {
                    "data": [
                        {
                            "name": device_name,
                            "vdom": "root"
                        }
                    ],
                    "url": f"/pm/config/adom/root/obj/cli/template-group/{temp_name}/scope member"
                }
            ],
        }
        payload.update({"session": self.sessionid})
        # print(json.dumps(payload, indent=2))
        assigncli_template = session.post(url=self.base_url, json=payload, verify=False)
        return assigncli_template.json()["result"]

    @ensure_session
    def remove_cli_template(self, device_name, temp_name):
        session = self.session
        payload = {
            "method": "delete",
            "params": [
                {
                    "data": [
                        {
                            "name": device_name,
                            "vdom": "root"
                        }
                    ],
                    "url": f"/pm/config/adom/root/obj/cli/template-group/{temp_name}/scope member"
                }
            ],
        }
        payload.update({"session": self.sessionid})
        # print(json.dumps(payload, indent=2))
        assigncli_template = session.post(url=self.base_url, json=payload, verify=False)
        return assigncli_template.json()["result"]

    @ensure_session
    def assignpkg(self, device_name):
        session = self.session
        payload = {
            "method": "add",
            "params": [
                {
                    "data": [
                        {
                            # "name": "default",
                            # "scope member": [
                            # {
                            "name": device_name,
                            "vdom": "root"
                            # }
                            # ],
                            # "type": "pkg"
                        }
                    ],
                    "url": "/pm/pkg/adom/root/Store Firewall Policy/scope member"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        assignpkg = session.post(url=self.base_url, json=payload, verify=self.verify)
        return assignpkg.json()

    @ensure_session
    def install_dev(self, device_name):
        session = self.session
        payload = {
            "method": "exec",
            "params": [
                {
                    "data": {
                        "adom": "root",
                        "dev_rev_comments": "test_DB",
                        "flags": [
                            "{option}"
                        ],
                        "scope": [
                            {
                                "name": device_name,
                                "vdom": "root"
                            }
                        ]
                    },
                    "url": "/securityconsole/install/device"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        install_dev = session.post(url=self.base_url, json=payload, verify=self.verify)
        return install_dev.json()

    @ensure_session
    def create_script(self, name, script_content, target: int = 0):
        session = self.session
        payload = \
            {
                "method": "add",
                "params": [{"url": f"/dvmdb/adom/{self.adom}/script/",
                            "data": {"name": name, "content": script_content, "target": target, "type": 1}}],
                "session": self.sessionid
            }
        create_script = session.post(
            url=self.base_url, json=payload, verify=self.verify)
        return create_script.json()["result"]

    @ensure_session
    def run_cli_script(self, device_name, scriptname):
        session = self.session
        payload = {
            "method": "exec",
            "params": [
                {
                    "data": {
                        "adom": "root",
                        "scope":
                            {
                                "name": device_name,
                                "vdom": "root"
                            }
                        ,
                        "script": scriptname
                    },
                    "url": "/dvmdb/adom/root/script/execute"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        run_cli_script = session.post(url=self.base_url, json=payload, verify=self.verify)
        return run_cli_script.json()

    @ensure_session
    def installpolicy(self, device_name):
        session = self.session
        payload = {
            "method": "exec",
            "params": [
                {
                    "data": {
                        "adom": "root",
                        "flags": [
                            "none"
                        ],
                        "pkg": "Store Firewall Policy",
                        "scope": [
                            {
                                "name": device_name,
                                "vdom": "root"
                            }
                        ]
                    },
                    "url": "/securityconsole/install/package"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        installpolicy = session.post(url=self.base_url, json=payload, verify=self.verify)
        return installpolicy.json()

    @ensure_session
    def printer_mapping(self, device_name, printer_ip):
        session = self.session
        null = None
        payload = {
            "method": "add",
            "params": [
                {
                    "url": "pm/config/adom/root/obj/firewall/address/PRINTER/dynamic_mapping",
                    "data": [
                        {
                            "_scope": [
                                {
                                    "name": device_name,
                                    "vdom": "root"
                                }
                            ],
                            "subnet": [
                                printer_ip,
                                "255.255.255.255"
                            ]
                        }
                    ],
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        printer_mapping = session.post(url=self.base_url, json=payload, verify=self.verify)
        return printer_mapping.json()

    @ensure_session
    def vlan_mapping(self, device_name, vlan_ip):
        session = self.session
        null = None
        payload = {
            "method": "add",
            "params": [
                {
                    "url": "pm/config/adom/root/obj/firewall/ippool/VLAN23_NAT/dynamic_mapping",
                    "data": [
                        {
                            "_scope": [
                                {
                                    "name": device_name,
                                    "vdom": "root"
                                }
                            ],
                            "endip": vlan_ip,
                            "startip": vlan_ip,
                        }
                    ]
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        printer_mapping = session.post(url=self.base_url, json=payload, verify=self.verify)
        return printer_mapping.json()

    @ensure_session
    def add_metavariable(self, dev_name, var_name, var_value):
        payload = {
            "method": "add",
            "params": [
                {
                    "data": [
                        {
                            "_scope": [
                                {
                                    "name": dev_name,
                                    "vdom": "global"
                                }
                            ],
                            "value": str(var_value)
                        }
                    ],
                    "url": f"/pm/config/adom/root/obj/fmg/variable/{var_name}/dynamic_mapping"
                }
            ],
            "session": "string",
            "id": 1
        }
        payload.update({"session": self.sessionid})
        response = requests.post(url=self.base_url, json=payload, verify=self.verify)
        return response.json()

    def check_system_status(self):
        payload = {
            "method": "get",
            "params": [
                {
                    "url": "/sys/status"
                }
            ],
            "session": "string"
        }
        payload.update({"session": self.sessionid})
        response = self.session.post(url=self.base_url, json=payload, verify=self.verify)
        return response

    def check_login(self):
        try:
            response = self.check_system_status()
            if response.status_code == 200 and response.json().get('result', [{}])[0].get('status', {}).get(
                    'code') == 0:
                return True
            else:
                self.login()
                # Instead of returning False, perform another status check after re-login
        except Exception as e:
            self.login()  # Attempt to login again if there's an exception

        # Perform a final status check after re-login attempt
        final_check = self.check_system_status()
        if final_check.status_code == 200 and final_check.json().get('result', [{}])[0].get('status', {}).get(
                'code') == 0:
            return True
        else:
            logging.error("Session invalid after multiple login attempts!")
            return False


if __name__ == "__main__":
    fmg = FortiManager("204.76.254.195", "mmarcotte", "qL2l5h7we34K", adom="root")
    dev_name = 'CHS-0575'
    try:
        if str(fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace('"',
                                                                                               '').strip() == 'v7.0.11':
            print(Fore.GREEN + "v7.0.11" + Style.RESET_ALL)
        else:
            print(
                Fore.RED + str(
                    fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace(
                    '"',
                    '') + Style.RESET_ALL)
    except:
        print(Fore.RED + "Unable to connect to device" + Style.RESET_ALL)
    dev_name = 'WHBM-3206'
    try:
        if str(fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace('"',
                                                                                               '').strip() == 'v7.0.11':
            print(Fore.GREEN + "v7.0.11" + Style.RESET_ALL)
        else:
            print(
                Fore.RED + str(
                    fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace(
                    '"',
                    '') + Style.RESET_ALL)
    except:
        print(Fore.RED + "Unable to connect to device" + Style.RESET_ALL)

