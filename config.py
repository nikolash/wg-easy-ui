# ~~~~~~~~~~~~~~ Configuration

# If instance/config.py exisits, individual values will be overwritten

# Mullvad private key. Install Mullvad according to https://mullvad.net/en/help/wireguard-and-mullvad-vpn/ and extract private key from one of the generated interfaces in /etc/wireguard
MULLVAD_PRIVATE_KEY = "" # Replace with your private key 

VPN_INTERFACE_US = "tun0-us" # This interface needs to exist in /etc/wireguard 
VPN_INTERFACE_UK = "tun0-uk" # This interface needs to exist in /etc/wireguard 

VPN_INTERFACE_CUSTOM = "tun0" # This interface will be created by wg-easy-ui if a custom server is selected  

# ~~~~~~~~~~~~~~ Usually no need to change

# Mullvad server API, does not need to be changed
MULLVAD_SERVER_LIST_API = "https://api.mullvad.net/www/relays/all/" 

# Mullvad DNS server, does not need to be changed
MULLVAD_DNS = "193.138.218.74" 

# Mullvad endpoint port, does not need to be changed
MULLVAD_SERVER_PORT = "51820" 

# Local IP for wireguard tunnel, you can choose any IP that does not interfere with your local IP subnet
MULLVAD_ADDRESS = "10.66.87.38/32" 