
# Chico's Staging Tool

## Overview

**Chico's Staging Tool** is a graphical utility designed to streamline the process of staging FortiManager devices, specifically for Chico's store networks. This tool provides a GUI for device configuration, management, and metadata assignment, helping users manage multiple devices through an easy-to-use interface.

## Features

- **FortiManager Integration**: Manages device connections and configurations within FortiManager.
- **SmartSheet Data Extraction**: Pulls relevant data from a designated SmartSheet for streamlined metadata management.
- **Secure Credential Management**: Stores credentials securely, using base64 obfuscation for sensitive data.
- **Device Metadata Assignment**: Adds various metadata fields for device configuration, including IP addresses, network details, and VLAN mappings.
- **Automation for Consistency**: Automatically assigns templates, policies, and metadata, reducing manual work and potential for errors.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/YOURUSERNAME/Chicos-Staging-Tool.git
    cd Chicos-Staging-Tool
    ```

2. **Install Required Packages**:
   Use the requirements file to install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   - Add your `SMARTSHEET_ACCESS_TOKEN` to an `.env` file or directly in the code to access SmartSheet data.
   - Ensure FortiManager credentials are available or enter them during each session.

## Usage

1. **Run the Tool**:
    ```bash
    python GUI.py
    ```

2. **Login**: Enter FortiManager credentials when prompted. Credentials will be stored securely for future sessions.

3. **Enter Account Numbers**: Input store account numbers for the devices you wish to configure.

4. **Follow the Instructions**:
   The GUI guides you through device metadata assignment, policy assignment, and template application. For advanced functions like template removal and VLAN mapping, follow the on-screen steps.

## Files

- **GUI.py**: Main executable, initializes the customtkinter GUI and manages device configuration functions.
- **API_Calls.py**: Handles all FortiManager API interactions, including device status checks, template assignment, and metadata updates.
- **requirements.txt**: Lists all libraries required by the tool.

## Key Classes and Functions

### `FortiManager` Class (API_Calls.py)
Handles FortiManager operations such as login, logout, device management, and status checking.

- **`login()`**: Authenticates with FortiManager and establishes a session.
- **`logout()`**: Ends the session with FortiManager.
- **`getstatus()`**: Fetches the status of a device in FortiManager.
- **`add_model_device()`**: Adds a new device to FortiManager, including metadata for configuration.
- **`assigncli_template()` / `remove_cli_template()`**: Assigns or removes CLI templates to/from devices.
- **`installpolicy()`**: Installs a predefined policy package on a device.
- **`printer_mapping()` / `vlan_mapping()`**: Configures device IP and VLAN mappings.
- **`run_cli_script()`**: Runs CLI scripts on a device.

### Helper Functions
Several helper functions in `GUI.py` provide essential utilities:
- **`encrypt()` / `decrypt()`**: Obfuscates and retrieves stored credentials.
- **`jprint()`**: Formats JSON responses for readability.
- **`getCreds()`**: Prompts for FortiManager credentials if not stored.

## License

This project is for internal use by Granite Telecommunications and should not be distributed outside the company.
