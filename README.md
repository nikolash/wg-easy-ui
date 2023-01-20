
# wg-easy-ui

Easy-to-use, girlfriend/wife-compatible wireguard web interface to operate a local VPN gateway.

Created to serve one specific use case: to conveniently operate a LAN-only VPN gateway (e.g. run on a raspberry pi) for devices within the LAN (e.g. an Apple TV). The interface easily lets you start and stop remote connections. This is useful if you live abroad and want to give your girlfriend/wife an easy way to connect said devices to specific countries that may have geo-locked streaming services without the need to ssh into the server every time and do this manually. Written in python and flask.


## Features

- Two favorite connection profiles for two locations (currently US and UK)
- Full integration into Mullvad VPN API
- Detects state of the connection and adapts the interface accordingly, No local database is needed, everything is operated via wireguard commands.

What this is not:
- There is no user credential checks whatsoever, everybody can access the interface (if that is what you need, you may still use iptables to do so)
- Also not optimized for performance, rather than being minimalistic. No database or caching is used in anticipation that the interface will only be used every so often

Limitations:
- Currently only runs with Mullvad VPN (which I highly recommend, even for streaming applications)
## Screenshots

![Home Screen](https://user-images.githubusercontent.com/646567/213718405-40b42193-0e79-4a44-b886-b62ad1fd3d33.png)

![Standard VPN Connection](https://user-images.githubusercontent.com/646567/213703656-d536bc27-9ceb-4803-bb65-dc467397cfef.png)

![Custom VPN Connection](https://user-images.githubusercontent.com/646567/213703652-6b12390c-f8db-4362-bea3-af96e98852b5.png)



## Installation

- Setup Wireguard and Mullvad (the interface currently only works with Mullvad) as described here: https://mullvad.net/en/help/wireguard-and-mullvad-vpn/
- Create two connection profiles within /etc/wireguard: tun0-us and tun0-uk (names can be changed in config.py). These will be used by the correspondent options on the GUI. Note: If a custom connection is being created, /etc/wireguard/tun0.conf will be created with the respective information in it. It will be overwritten every time a custom connection is started
- Install a WSGI container like gunicorn, make sure the process can execute wg and wg-quick commands
- Install flask: (pip install -U Flask)
- Edit config.py file, currently only MULLVAD_PRIVATE_KEY needs to be adapted, the other values can stay the way they are. The value can be extracted after the installation from one of the profiles in /etc/wireguard
- Deploy the application to the WSGI server (app.py, config.py as well as 'static' and 'templates' folders)
