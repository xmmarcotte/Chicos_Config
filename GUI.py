from base64 import b64encode, b64decode
import customtkinter
import API_Calls
import json
import smartsheet
import os
import sys
from colorama import init
from colorama import Fore, Back, Style
import time
import ctypes
import msvcrt
import win32gui
import win32con
import win32api
import re

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
os.system("mode con: cols=95 lines=30")


def center_console_on_current_monitor():
    # Get the handle of the console window
    console_handle = win32gui.GetForegroundWindow()

    # Get the size of the console window
    console_rect = win32gui.GetWindowRect(console_handle)
    console_width = console_rect[2] - console_rect[0]
    console_height = console_rect[3] - console_rect[1]

    # Get the current position of the mouse cursor
    mouse_x, mouse_y = win32api.GetCursorPos()

    # Determine which monitor contains the cursor
    monitor_info = win32api.MonitorFromPoint((mouse_x, mouse_y), win32con.MONITOR_DEFAULTTONEAREST)

    # Get the work area (usable area excluding taskbars etc.) of the monitor
    monitor_area = win32api.GetMonitorInfo(monitor_info)['Work']

    # Calculate the center position on the monitor
    monitor_center_x = monitor_area[0] + (monitor_area[2] - monitor_area[0]) // 2
    monitor_center_y = monitor_area[1] + (monitor_area[3] - monitor_area[1]) // 2

    new_x = monitor_center_x - console_width // 2
    new_y = monitor_center_y - console_height // 2

    # Move the console window
    win32gui.SetWindowPos(console_handle, win32con.HWND_TOP, new_x, new_y, console_width, console_height, 0)

    # Bring the console window to focus
    win32gui.SetForegroundWindow(console_handle)


def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def show_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)


def obfuscate(plainText):
    plainBytes = plainText.encode('ascii')
    encodedBytes = b64encode(plainBytes)
    encodedText = encodedBytes.decode('ascii')
    return encodedText


def deobfuscate(obfuscatedText):
    obfuscatedBytes = obfuscatedText.encode('ascii')
    decodedBytes = b64decode(obfuscatedBytes)
    decodedText = decodedBytes.decode('ascii')
    return decodedText


def encrypt(pw):
    encrypted = obfuscate(obfuscate(obfuscate(obfuscate(obfuscate(pw)))))
    return encrypted


def decrypt(pw):
    decrypted = deobfuscate(deobfuscate(deobfuscate(deobfuscate(deobfuscate(pw)))))
    return decrypted


def getpass_with_asterisks(prompt="Password: "):
    print(prompt, end='', flush=True)
    buf = ""
    while True:
        ch = msvcrt.getch()
        if ch in [b'\r', b'\n']:
            print('')
            break
        elif ch == b'\x08':  # Backspace
            if len(buf) > 0:
                buf = buf[:-1]
                print('\b \b', end='', flush=True)
        else:
            buf += ch.decode('utf-8')
            print('*', end='', flush=True)
    return buf


def getCreds():
    global user_name, password
    console_handle = win32gui.GetForegroundWindow()
    win32gui.SetForegroundWindow(console_handle)

    print("Enter your FortiManager credentials\n")
    user_name = input("Username: ")
    password = getpass_with_asterisks("Password: ")


def login():
    global user_name, password
    if os.path.exists("credentials.txt"):
        creds = open('credentials.txt', 'r')
        creds.seek(0)
        lines = creds.readlines()
        user_name = lines[0].strip()
        password = lines[1].strip()
        try:
            user_name = decrypt(user_name)
            creds.close()
        except:
            creds.close()
            pass
        try:
            password = decrypt(password)
            creds.close()
        except:
            creds.close()
            pass
    else:
        getCreds()

    success = False

    while not success:
        try:
            fmg = API_Calls.FortiManager(host="204.76.254.195", username=user_name, password=password, adom="root")
            fmg.login()
            success = True
            fmg.logout()

            if not os.path.exists("credentials.txt"):
                encrypted_un = encrypt(user_name)
                encrypted_pass = encrypt(password)
                with open('credentials.txt', 'w') as fh:
                    fh.write(f"{encrypted_un}\n")
                    fh.write(f"{encrypted_pass}")
        except:
            if os.path.exists("credentials.txt"):
                os.remove("credentials.txt")
            os.system('cls')
            print("Invalid credentials, please try again...")
            time.sleep(2)
            os.system('cls')
            getCreds()


def get_value(x):
    zero_val = False
    value = row.get_column(column_map[x]).value
    if str(value).startswith("0"):
        zero_val = True
    try:
        value = float(value)
        if value.is_integer():
            value = int(value)
    except:
        pass
    if zero_val:
        value = "0" + str(value)
    else:
        value = str(value)
    return value


def jprint(obj):
    try:
        if str(json.loads(json.dumps(obj, indent=2))[0]['status']['message']) == "OK":
            print(
                " " + Fore.LIGHTGREEN_EX + str(
                    json.loads(json.dumps(obj, indent=2))[0]['status']['message']) + Style.RESET_ALL)
        else:
            print(" " + Fore.LIGHTRED_EX + str(
                json.loads(json.dumps(obj, indent=2))[0]['status']['message']) + Style.RESET_ALL)
    except:
        try:
            if str(json.loads(json.dumps(obj, indent=2))['result'][0]['status']['message']) == "OK":
                print(" " + Fore.LIGHTGREEN_EX + str(
                    json.loads(json.dumps(obj, indent=2))['result'][0]['status']['message']) + Style.RESET_ALL)
            else:
                print(" " + Fore.LIGHTRED_EX + str(
                    json.loads(json.dumps(obj, indent=2))['result'][0]['status']['message']) + Style.RESET_ALL)
        except:
            print(str(json.dumps(obj, indent=2)))


def jprint_raw(obj):
    print(str(json.dumps(obj, indent=2)))


def get_var(acct):
    global fg_sn, fs_sn, fex_sn, BB1_DESC, BB1_GW, BB1_IP, BB1_MASK, BB2_DESC, BB2_GW, BB2_IP, BB2_MASK, MPLS_GW, \
        MPLS_IP, NETWORK_CORP, NETWORK_LOOPBACK, NETWORK_MISC, NETWORK_STORE, NETWORK_WIRELESS, STORE_NUMBER, \
        VLAN23_NAT, PRINTER, dev_name, template, sheet, row, dev_name
    for row in sheet.rows:
        if get_value('Services Child Account') == acct:
            fg_sn = get_value('FortiGate S/N').upper()
            fs_sn = get_value('FortiSwitch S/N').upper()
            fex_sn = get_value('FEX S/N').upper()
            BRAND = get_value('Banner')
            if BRAND.lower().startswith("ch"):
                BRAND = 'CHS'
            if BRAND.lower().startswith("so"):
                BRAND = 'SOMA'
            if BRAND.lower().startswith("wh"):
                BRAND = 'WHBM'
            BB1_DESC = get_value('BB1_DESC')
            BB1_GW = get_value('BB1_GW')
            BB1_IP = get_value('BB1_IP')
            BB1_MASK = get_value('BB1_MASK')
            BB2_DESC = get_value('BB2_DESC')
            BB2_GW = get_value('BB2_GW')
            BB2_IP = get_value('BB2_IP')
            BB2_MASK = get_value('BB2_MASK')
            MPLS_GW = get_value('MPLS_GW')
            MPLS_IP = get_value('MPLS_IP')
            NETWORK_CORP = get_value('NETWORK_CORP')
            NETWORK_LOOPBACK = get_value('NETWORK_LOOPBACK')
            NETWORK_MISC = get_value('NETWORK_MISC')
            NETWORK_STORE = get_value('NETWORK_STORE')
            NETWORK_WIRELESS = get_value('NETWORK_WIRELESS')
            STORE_NUMBER = str(get_value('Store Number')).zfill(4)
            VLAN23_NAT = get_value('VLAN23_NAT')
            PRINTER = get_value('PRINTER')
            dev_name = f"{BRAND}-{str(STORE_NUMBER).zfill(4)}"
            if str(BB1_IP) != "None" and str(BB2_IP) != "None":
                temp_type = "BB1+BB2+LTE"
            elif str(BB1_IP) != "None" and str(BB2_IP) == "None" and str(MPLS_IP) == "None":
                temp_type = "BB1+LTE"
            elif str(BB1_IP) != "None" and str(MPLS_IP) != "None" and str(BB2_IP) == "None":
                temp_type = "BB1+MPLS+LTE"
            elif MPLS_IP != "None" and BB1_IP == "None" and BB2_IP == "None":
                temp_type = "MPLS+LTE"
            else:
                print(f"IPs missing for {acct}, unable to choose template")
            if BRAND == "CHS":
                template = f"*Router_Chicos_{temp_type}"
            elif BRAND == "SOMA":
                template = f"*Router_Soma_{temp_type}"
            elif BRAND == "WHBM":
                template = f"*Router_WHBM_{temp_type}"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def center_win(root):
    mouse_x, mouse_y = win32api.GetCursorPos()
    monitor_info = win32api.MonitorFromPoint((mouse_x, mouse_y), win32con.MONITOR_DEFAULTTONEAREST)
    monitor_area = win32api.GetMonitorInfo(monitor_info)['Work']
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = monitor_area[0] + (monitor_area[2] - monitor_area[0] - w) // 2
    y = monitor_area[1] + (monitor_area[3] - monitor_area[1] - h) // 2
    root.geometry(f'+{x}+{y}')


def exitProg():
    sys.exit()


def extract_account_numbers(raw_input):
    # Remove any store identifiers (e.g., "CHS-0069 - ") and split by commas, spaces, or line breaks
    stripped_input = re.sub(r"[A-Za-z-]+\s*-\s*", "", raw_input)
    potential_numbers = re.split(r"[,\s]+", stripped_input)

    # Filter out only the valid 8-digit account numbers that start with '0'
    account_numbers = [num.strip() for num in potential_numbers if num.startswith('0') and len(num) == 8]
    return account_numbers


def get_account_numbers(root, on_accounts_entered_callback):
    account_numbers = []

    def on_submit(event=None):
        nonlocal account_numbers
        raw_input = account_entry.get("1.0", 'end-1c')
        account_numbers = extract_account_numbers(raw_input)
        input_window.destroy()
        on_accounts_entered_callback(account_numbers, skip_to_phase_2=False)

    def on_jump_to_phase_2(event=None):
        nonlocal account_numbers
        raw_input = account_entry.get("1.0", 'end-1c')
        account_numbers = extract_account_numbers(raw_input)
        input_window.destroy()
        on_accounts_entered_callback(account_numbers, skip_to_phase_2=True)

    os.system('cls')
    print("Use the pop-up window to enter account numbers.\n\nThey can be separated by any combination of line breaks, "
          "spaces, or commas.")
    input_window = customtkinter.CTkToplevel(root)
    input_window.title("Chico's Staging Tool")
    granite_icon = resource_path("granite.ico")
    input_window.after(201, lambda: input_window.wm_iconbitmap(granite_icon))
    input_window.attributes('-alpha', 0.95)
    center_win(input_window)

    input_window.grid_rowconfigure(1, weight=1)
    input_window.grid_columnconfigure(0, weight=1)

    label = customtkinter.CTkLabel(input_window, text='Please enter the account number(s):')
    label.grid(row=0, column=0, pady=(20, 0), sticky="ew")

    account_entry = customtkinter.CTkTextbox(input_window, width=300, height=300)
    account_entry.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

    submit_button = customtkinter.CTkButton(input_window, text="Submit", command=on_submit)
    submit_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    jump_to_phase_2_button = customtkinter.CTkButton(input_window, text="Jump to Phase 2", command=on_jump_to_phase_2)
    jump_to_phase_2_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

    input_window.bind('<Return>', on_submit)
    input_window.protocol("WM_DELETE_WINDOW", exitProg)

    input_window.mainloop()
    return account_numbers


def processing_msg(sec):
    global count
    sys.stdout.write("Processing")
    sys.stdout.flush()
    for i in range(sec + count):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('\r' + ' ' * 20 + '\r')
    sys.stdout.flush()


def build_config_dict(acct):
    get_var(acct)

    config_dict = {
        'STORE_SW01_SN': fs_sn,
        'BB1_DESC': BB1_DESC,
        'BB1_GW': BB1_GW,
        'BB1_IP': BB1_IP,
        'BB1_MASK': BB1_MASK,
        'BB2_DESC': BB2_DESC,
        'BB2_GW': BB2_GW,
        'BB2_IP': BB2_IP,
        'BB2_MASK': BB2_MASK,
        'MPLS_GW': MPLS_GW,
        'MPLS_IP': MPLS_IP,
        'NETWORK_CORP': NETWORK_CORP,
        'NETWORK_LOOPBACK': NETWORK_LOOPBACK,
        'NETWORK_MISC': NETWORK_MISC,
        'NETWORK_STORE': NETWORK_STORE,
        'NETWORK_WIRELESS': NETWORK_WIRELESS,
        'STORE_NUMBER': STORE_NUMBER
    }

    return config_dict


def run_fortimanager_operations(accounts, skip_to_phase_2):
    global count, user_name, password
    failed_accounts = []
    count = -1
    for i in accounts:
        count += 1

    fmg = API_Calls.FortiManager("204.76.254.195", user_name, password, adom="root")
    try:
        fmg.logout()
    except:
        ...
    fmg.check_login()
    if not skip_to_phase_2:
        for child_account in accounts:
            try:
                get_var(child_account)
                sys.stdout.write(f"Adding {dev_name} ({fg_sn}) to Fortimanager and assigning meta-fields... ")
                jprint(
                    fmg.add_model_device(device_name=dev_name, serial_num=fg_sn, description=child_account,
                                         BB1_DESC=BB1_DESC,
                                         BB1_GW=BB1_GW, BB1_IP=BB1_IP, BB1_MASK=BB1_MASK, BB2_DESC=BB2_DESC,
                                         BB2_GW=BB2_GW,
                                         BB2_IP=BB2_IP, BB2_MASK=BB2_MASK, MPLS_GW=MPLS_GW, MPLS_IP=MPLS_IP,
                                         NETWORK_CORP=NETWORK_CORP, NETWORK_LOOPBACK=NETWORK_LOOPBACK,
                                         NETWORK_MISC=NETWORK_MISC,
                                         NETWORK_STORE=NETWORK_STORE, NETWORK_WIRELESS=NETWORK_WIRELESS,
                                         STORE_NUMBER=STORE_NUMBER, STORE_SW01_SN=fs_sn))
                time.sleep(2)
            except Exception:
                failed_accounts.append(child_account)
                count -= 1
        for failed_account in failed_accounts:
            accounts.remove(failed_account)
        if accounts:
            processing_msg(10)

            for child_account in accounts:
                get_var(child_account)
                config_dict = build_config_dict(child_account)
                for var_name, var_value in config_dict.items():
                    if var_value is not None and var_value != "None":
                        sys.stdout.write(f"Adding metadata variable {var_name}: {var_value} for {dev_name}... ")
                        jprint(fmg.add_metavariable(dev_name, var_name, var_value))
                        time.sleep(2)

            for child_account in accounts:
                get_var(child_account)
                sys.stdout.write(f"Mapping {dev_name} printer to {PRINTER}... ")
                jprint(fmg.printer_mapping(device_name=dev_name, printer_ip=PRINTER))
                time.sleep(2)
            processing_msg(7)

            for child_account in accounts:
                get_var(child_account)
                sys.stdout.write(f"Mapping {dev_name} VLAN 23 NAT to {VLAN23_NAT}... ")
                jprint(fmg.vlan_mapping(device_name=dev_name, vlan_ip=VLAN23_NAT))
                time.sleep(2)
            processing_msg(7)

            for child_account in accounts:
                get_var(child_account)
                sys.stdout.write(f"Assigning policy package for {dev_name}... ")
                jprint(fmg.assignpkg(dev_name))
                time.sleep(2)
            processing_msg(7)

        print("\nPhase 1 complete:\n-----------------")
        for child_account in accounts:
            get_var(child_account)
            print(dev_name, "-", Fore.LIGHTBLUE_EX + child_account + Fore.RESET)
        if failed_accounts:
            print("\nPhase 1 failed:\n---------------")
            for child_account in failed_accounts:
                print(Fore.LIGHTRED_EX + str(child_account) + Fore.RESET)
            print("\nCheck the smartsheet and stage any failed devices manually.")

    if accounts:
        input("\nPress enter to start phase 2!")
        print(f"""\n1. Connect the devices that {Fore.LIGHTGREEN_EX}completed{Style.RESET_ALL} phase 1.
2. Wait until the {Fore.LIGHTBLUE_EX}status lights{Style.RESET_ALL} are {Fore.LIGHTGREEN_EX}lit{Style.RESET_ALL} and the devices are up in FMG.
3. Verify the {Fore.LIGHTBLUE_EX}auto-link{Style.RESET_ALL} task in task monitor is {Fore.LIGHTGREEN_EX}completed{Style.RESET_ALL} for all devices.
   (this may take a few minutes - conflict status/failure is normal)\n""")
        input("Press enter to continue...")
        print(
            f'\n***Firmware check***\n If the device isn\'t on {Fore.LIGHTGREEN_EX}v7.0.11{Style.RESET_ALL}, '
            'insert firmware USB\n and power cycle the device before continuing.\n')
        firmware_up = False
        while not firmware_up:
            fmg.check_login()
            print('')
            for child_account in accounts:
                get_var(child_account)
                sys.stdout.write(dev_name + ": ")
                try:
                    if str(fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace('"',
                                                                                                           '').strip() == 'v7.0.11':
                        print(Fore.LIGHTGREEN_EX + "v7.0.11" + Style.RESET_ALL)
                    else:
                        print(
                            Fore.LIGHTRED_EX + str(
                                fmg.getstatus(dev_name)['result'][0]['data'][0]['response']['version']).replace(
                                '"',
                                '') + Style.RESET_ALL)
                except:
                    print(Fore.LIGHTRED_EX + "Unable to connect to device" + Style.RESET_ALL)
            print('')
            is_firmware_up = input("Are all devices up to date (y/n)? (Answer 'n' to check again) ")
            if is_firmware_up.lower() in ('yes', 'y', 'yup'):
                firmware_up = True

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Running purge_db script on {dev_name}... ")
            jprint(fmg.run_cli_script(dev_name, scriptname="purge_db"))
            time.sleep(2)
        processing_msg(10)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Assigning {template} template to {dev_name}... ")
            jprint(fmg.assigncli_template(dev_name, template))
            time.sleep(2)
        processing_msg(5)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Installing from device database for {dev_name}... ")
            jprint(fmg.install_dev(dev_name))
            time.sleep(2)
        processing_msg(45)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Installing Store Firewall Policy on {dev_name}... ")
            jprint(fmg.installpolicy(dev_name))
            time.sleep(2)
        processing_msg(30)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Removing {template} assignment from {dev_name}... ")
            jprint(fmg.remove_cli_template(dev_name, template))
            time.sleep(2)
        processing_msg(5)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Running 61F Post-Run script on {dev_name}... ")
            jprint(fmg.run_cli_script(dev_name, scriptname="61F Post-Run"))
            time.sleep(2)
        processing_msg(30)

        fmg.check_login()
        for child_account in accounts:
            get_var(child_account)
            sys.stdout.write(f"Installing Store Firewall Policy on {dev_name}... ")
            jprint(fmg.installpolicy(dev_name))
            time.sleep(2)
        processing_msg(30)

        sys.stdout.write("Logging out... ")
        jprint(fmg.logout())
        try:
            fmg.logout()
        except:
            ...

        print("\nPhase 2 complete:\n-----------------")
        for child_account in accounts:
            get_var(child_account)
            print(dev_name, "-", Fore.LIGHTBLUE_EX + str(child_account) + Fore.RESET)
        print(f"""\nVerification steps:
-------------------
1. Check the task monitor for any errors
2. Check the row in device manager for the following:
    a. Config status should be {Fore.LIGHTBLUE_EX + "Synchronized" + Fore.RESET} or {Fore.LIGHTBLUE_EX + "Auto-update" + Fore.RESET} with a {Fore.LIGHTGREEN_EX + "green" + Fore.RESET} check mark
    b. Host Name should be the store name and number (e.g. {Fore.LIGHTBLUE_EX + "CHS-1234" + Fore.RESET})
    c. Policy Package Status should be {Fore.LIGHTBLUE_EX + "Store Firewall Policy" + Fore.RESET} with a {Fore.LIGHTGREEN_EX + "green" + Fore.RESET} check mark
3. NOTE: You may occasionally see some steps fail in the task monitor. As long as everything
   in step 2 is correct and the final installation process is successful, the devices have
   been configured properly. """)




    else:
        show_exit_window()


def show_exit_window():
    exit_win = customtkinter.CTk()
    exit_win.title("Exit")
    granite_icon = resource_path("granite.ico")
    after1 = exit_win.after(201, lambda: exit_win.wm_iconbitmap(granite_icon))
    root.after_cancel(after1)
    exit_win.geometry('300x100')
    center_win(exit_win)

    def on_exit():
        sys.exit()

    customtkinter.CTkLabel(exit_win, text="Click the button to exit the application.").pack(pady=10)
    exit_button = customtkinter.CTkButton(exit_win, text="Exit", command=on_exit)
    exit_button.pack(pady=10)
    exit_win.mainloop()


sheet_id = 6783282322558852
SMARTSHEET_ACCESS_TOKEN = 'vrwMoy8Wy9APWHRxhWvWkoo0k0GuYs4npJ2Kw'
smart = smartsheet.Smartsheet(SMARTSHEET_ACCESS_TOKEN)
smart.errors_as_exceptions(True)
sheet = smart.Sheets.get_sheet(sheet_id)
column_map = {column.title: column.id for column in sheet.columns}
customtkinter.set_appearance_mode('dark')
accounts = []


def main():
    global root
    center_console_on_current_monitor()
    show_console()
    os.system('cls')
    init(convert=False, strip=False)
    print(Fore.RED + """    
    
                         ▄████▄   ██░ ██  ██▓ ▄████▄   ▒█████    ██████            
                        ▒██▀ ▀█  ▓██░ ██▒▓██▒▒██▀ ▀█  ▒██▒  ██▒▒██    ▒            
                        ▒▓█    ▄ ▒██▀▀██░▒██▒▒▓█    ▄ ▒██░  ██▒░ ▓██▄              
                        ▒▓▓▄ ▄██▒░▓█ ░██ ░██░▒▓▓▄ ▄██▒▒██   ██░  ▒   ██▒           
                        ▒ ▓███▀ ░░▓█▒░██▓░██░▒ ▓███▀ ░░ ████▓▒░▒██████▒▒           
                        ░ ░▒ ▒  ░ ▒ ░░▒░▒░▓  ░ ░▒ ▒  ░░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░           
                          ░  ▒    ▒ ░▒░ ░ ▒ ░  ░  ▒     ░ ▒ ▒░ ░ ░▒  ░ ░           
                        ░    ░    ░  ░░ ░ ▒ ░░        ░ ░ ░ ▒  ░  ░  ░             
                    ██████ ▄▄▄█████▓ ▄▄▄    ░   ▄████  ██▓ ███▄    █ ░ ▄████ 
                  ▒██    ▒ ▓  ██▒ ▓▒▒████▄     ██▒ ▀█▒▓██▒ ██ ▀█   █  ██▒ ▀█▒
                  ░ ▓██▄   ▒ ▓██░ ▒░▒██  ▀█▄  ▒██░▄▄▄░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
                    ▒   ██▒░ ▓██▓ ░ ░██▄▄▄▄██ ░▓█  ██▓░██░▓██▒  ▐▌██▒░▓█  ██▓
                  ▒██████▒▒  ▒██▒ ░  ▓█   ▓██▒░▒▓███▀▒░██░▒██░   ▓██░░▒▓███▀▒
                   ▒ ▒▓▒ ▒ ░  ▒ ░░    ▒▒   ▓▒█░ ░▒   ▒ ░▓  ░ ▒░   ▒ ▒  ░▒   ▒ 
                   ░ ░▒  ░ ░    ░      ▒   ▒▒ ░  ░   ░  ▒ ░░ ░░   ░ ▒░  ░   ░ 
                   ░  ░  ░    ░        ░   ▒   ░ ░   ░  ▒ ░   ░   ░ ░ ░ ░   ░ 
                      ░        ▄▄▄█████▓ ▒█████   ▒█████   ██▓      ░ ░     ░               
                               ▓  ██▒ ▓▒▒██▒  ██▒▒██▒  ██▒▓██▒        ░                    
                      ░        ▒ ▓██░ ▒░▒██░  ██▒▒██░  ██▒▒██░                            
                               ░ ▓██▓ ░ ▒██   ██░▒██   ██░▒██░        ░                   
                                 ▒██▒ ░ ░ ████▓▒░░ ████▓▒░░██████▒                        
                                 ▒ ░░   ░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒░▓  ▓                        
                                   ░      ░ ▒ ▒░   ░ ▒ ▒░ ░ ░ ▒  ░                        
                                 ░      ░ ░ ░ ▒  ░ ░ ░ ▒    ░ ░                           
                                            ░ ░      ░ ░      ░  ░""" + Fore.RESET)
    print("\n                                   Created by Mikey Marcotte")
    time.sleep(2)
    root = customtkinter.CTk()
    root.title("Chico's Staging Tool")
    granite_icon = resource_path("granite.ico")
    root.wm_iconbitmap(granite_icon)
    root.attributes('-alpha', 0.95)
    center_win(root)
    root.protocol("WM_DELETE_WINDOW", exitProg)
    root.withdraw()

    def on_accounts_entered(accounts, skip_to_phase_2):
        if accounts:
            os.system('cls')
            run_fortimanager_operations(accounts, skip_to_phase_2=skip_to_phase_2)
        else:
            os.system('cls')
            print("No accounts entered (╯°□°)╯_- ┻━┻")
            show_exit_window()

    time.sleep(2)
    os.system('cls')
    login()
    try:
        accounts = get_account_numbers(root, on_accounts_entered)
    except Exception as e:
        os.system('cls')
        print(Fore.LIGHTRED_EX + "Critical Failure! " + Fore.RESET +
              "Please screenshot the error below and send to Mikey Marcotte.")
        print(f"\n{e}")
    show_exit_window()

    root.mainloop()


if __name__ == "__main__":
    main()
