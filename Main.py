# -*- coding: utf-8 -*-

import os
import json
import time
import argparse

from Replay import Replay
from TCP.Crypto import Crypto
from twisted.internet import reactor
from TCP.Server.factory import ServerFactory
from TCP.Server.endpoint import ServerEndpoint
from TCP.Client.endpoint import ClientEndpoint

from UDP.protocol import UDPProtocol


def onClose(udp_protocol):
        print("[*] Closing proxy !")

        if udp_protocol is not None:
            udp_protocol.packetProcessor.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python proxy used to decrypt all clash royale game traffic')
    parser.add_argument('-v', '--verbose', help='print packet hexdump in console', action='store_true')
    parser.add_argument('-r', '--replay', help='save packets in replay folder', action='store_true')
    parser.add_argument('-u', '--udp', help='start the udp proxy', action='store_true')

    args = parser.parse_args()

    if os.path.isfile('config.json'):
        config = json.load(open('config.json'))

    else:
        print('[*] config.json is missing !')
        exit()

    crypto = Crypto(config['ServerKey'])
    replay = Replay(config['ReplayDirectory'])

    client_endpoint = ClientEndpoint(reactor, config['Hostname'], config['Port'])
    server_endpoint = ServerEndpoint(reactor, config['Port'])

    udp_protocol = UDPProtocol(config['UDPHost'], config['UDPPort'], replay) if args.udp else None
    server_endpoint.listen(ServerFactory(client_endpoint, udp_protocol, crypto, replay, args))

    print("[*] TCP Proxy is listening on {}:{}".format(server_endpoint.interface, server_endpoint.port))

    if udp_protocol is not None:
        udp_listener = reactor.listenUDP(config['UDPPort'], udp_protocol)
        udp_listener_host = udp_listener.getHost()

        print("[*] UDP Proxy is listening on {}:{}".format(udp_listener_host.host, udp_listener_host.port))

    reactor.addSystemEventTrigger('before', 'shutdown', onClose, udp_protocol)
    reactor.run()
