from flask import Flask, render_template, request, jsonify
import subprocess, re, requests, os, sys

# ~~~~~~~~~~~~~~ Init

app = Flask(__name__, instance_relative_config = os.path.exists("instance/config.py"))
app.config.from_pyfile("config.py") # Overwrite values from /instance/config.py

if app.config["MULLVAD_PRIVATE_KEY"] == "":
    print ("Mullvad private key missing. Please specify in config.py, otherwise wg-easy-ui cannot create custom connection profiles.")
    sys.exit(1)

# ~~~~~~~~~~~~~~ Routes

# JSON API
# api/vpn/
# 'action' start or stop via POST
@app.route('/api/vpn', methods = ['POST'])
def api_vpn():
    if request.method == 'POST':
        action = request.json.get('action')
        wg_interface = app.config["VPN_INTERFACE_US"] # For now, start always starts the US VPN

        if action == 'start':
            if get_vpn_active():
                # If VPN already up, generate error message
                action_response = "VPN already active, please stop service first."
            else:
                action_response = subprocess.run(["wg-quick", "up", wg_interface], stderr = subprocess.PIPE).stderr.decode()
            
            return jsonify({'status': 'success', 'response': action_response})
        elif action == 'stop':
            if get_vpn_active():
                action_response = subprocess.run(["wg-quick", "down", wg_interface], stderr = subprocess.PIPE).stderr.decode()
            else:
                action_response = "VPN is not up."
            
            return jsonify({'status': 'success', 'response': action_response})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid action, use start or stop.'})

# ############## Home ##############
@app.route("/")
def index():
    server_list = get_server_list() 
    wg_status = get_wg_status()
    active_host = None
    wg_interface = None

    if wg_status:
        wg_interface = wg_status["interface"]
        if wg_interface == app.config["VPN_INTERFACE_CUSTOM"]:
            # Find out connected hostname via peer public key
            active_server = next(filter(lambda x: x["type"] == "wireguard" and x["pubkey"] == wg_status["peer_pubkey"], server_list), None)
            active_host = active_server["hostname"]

    return render_template("index.html", wan_status = get_wan_status(), 
        wg_status = get_wg_status(), server_list = get_server_list(), wg_interface = wg_interface, selected_server = active_host)


# ############## Start VPN ##############
@app.route("/up", methods = ["POST"])
def wg_up():
    server_list = get_server_list() # Load early, needed in case of custom selection

    if get_vpn_active():
        # If VPN already up, generate error message
        action_response = "VPN already active, please stop service first."
    else:
        # Start VPN based on selected location
        vpn_location = request.form.get("vpn-location")
        wg_interface = None
        
        if vpn_location == "tun-us":
            wg_interface = app.config["VPN_INTERFACE_US"]
        elif vpn_location == "tun-uk":
            wg_interface = app.config["VPN_INTERFACE_UK"]
        elif vpn_location == "tun-custom":
            wg_interface = app.config["VPN_INTERFACE_CUSTOM"]
            
            selected_item = request.form["vpn-custom"]

            if len(selected_item) > 0:
                # Custom interface selected, create/update config file for current selection
                selected_server = next(filter(lambda x: x["hostname"] == selected_item, server_list), None)
                

                with open("/etc/wireguard/" + app.config["VPN_INTERFACE_CUSTOM"] + ".conf", "w") as file:
                    file.write("[Interface]\n")
                    file.write("PrivateKey = " + app.config["MULLVAD_PRIVATE_KEY"] + "\n")
                    file.write("Address = " + app.config["MULLVAD_ADDRESS"] + "\n")
                    file.write("DNS = " + app.config["MULLVAD_DNS"] + "\n")
                    file.write("\n")
                    file.write("[Peer]\n")
                    file.write("PublicKey = " + selected_server["pubkey"] + "\n")
                    file.write("Endpoint = " + selected_server["ipv4_addr_in"] + ":" + app.config["MULLVAD_SERVER_PORT"] + "\n")
                    file.write("AllowedIPs = 0.0.0.0/0")
            else: 
                action_response = "Please select a custom location in the dropdown."
                return render_template("index.html", wan_status = get_wan_status(), wg_status = get_wg_status(), 
                    action_response = action_response, server_list = server_list, wg_interface = wg_interface)
        else:
            wg_interface = app.config["VPN_INTERFACE_US"] # default with no selection is US
        
        action_response = subprocess.run(["wg-quick", "up", wg_interface], stderr = subprocess.PIPE).stderr.decode()

    return render_template("index.html", wan_status = get_wan_status(), wg_status = get_wg_status(), 
        action_response = action_response, server_list = server_list, 
        wg_interface = wg_interface, selected_server = request.form["vpn-custom"])

# ############## Stop VPN ##############
@app.route("/down", methods = ["POST"])
def wg_down():
    wg_status = get_wg_status()
    wg_interface = wg_status["interface"]
    
    if wg_status:
        if wg_interface == app.config["VPN_INTERFACE_US"] or wg_interface == app.config["VPN_INTERFACE_UK"] or wg_interface == app.config["VPN_INTERFACE_CUSTOM"]:
            action_response = subprocess.run(["wg-quick", "down", wg_status["interface"]], stderr = subprocess.PIPE).stderr.decode()
        else:
            action_response = "No US or UK VPN active, but another one: " + wg_status["interface"] + ". Will not stop this one, please consult Niko."
    else:
        # If VPN down, generate error message
        action_response = "VPN is not active."

    return render_template("index.html", wan_status = get_wan_status(), 
        action_response = action_response, server_list = get_server_list())

# ~~~~~~~~~~~~~~ Support Functions

# Load Mullvad server list
def get_server_list():
    response = requests.get(app.config["MULLVAD_SERVER_LIST_API"])
    server_list = {}
    if response.status_code == 200:
        server_list = response.json()
    else:
        print("Error accessing Mullvad API: ", response.status_code)
    return server_list

# Get public IP
def get_wan_status():
    wan_status = requests.get("https://ipapi.co/json/")
    return wan_status.json()


# Check if VPN is active (using wg show)
def get_vpn_active():
    wg_show = subprocess.run(["wg", "show"], stdout = subprocess.PIPE).stdout.decode()
    return wg_show

# Get wireguard status (using wg show) in array format
def get_wg_status():
    wg_show = subprocess.run(["wg", "show"], stdout = subprocess.PIPE).stdout.decode()
    wg_status = {}
    if len(wg_show) > 0:
        wg_status["interface"] = re.search(r"interface: (.*?)\n", wg_show).group(1)
        wg_status["endpoint"] = re.search(r"endpoint: (.*?)\n", wg_show).group(1)
        wg_status["latest_handshake"] = re.search(r"latest handshake: (.*?)\n", wg_show).group(1)
        wg_status["transfer"] = re.search(r"transfer: (.*?)\n", wg_show).group(1)
        wg_status["peer_pubkey"] = re.search(r"peer: (.*?)\n", wg_show).group(1)
    return wg_status    