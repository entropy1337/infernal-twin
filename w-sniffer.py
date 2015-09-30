from scapy.all import *

def insert_ap(pkt):
    ## Done in the lfilter param
    # if Dot11Beacon not in pkt and Dot11ProbeResp not in pkt:
    #     return
    bssid = pkt[Dot11].addr3
    if bssid in aps:
        return
    p = pkt[Dot11Elt]
    cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}"
                      "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
    ssid, channel = None, None
    crypto = set()
    while isinstance(p, Dot11Elt):
        if p.ID == 0:
            ssid = p.info
        elif p.ID == 3:
            channel = ord(p.info)
        elif p.ID == 48:
            crypto.add("WPA2")
        elif p.ID == 221 and p.info.startswith('\x00P\xf2\x01\x01\x00'):
            crypto.add("WPA")
        p = p.payload
    if not crypto:
        if 'privacy' in cap:
            crypto.add("WEP")
        else:
            crypto.add("OPN")
    print "NEW AP: %r [%s], channed %d, %s" % (ssid, bssid, channel,
                                               ' / '.join(crypto))
    aps[bssid] = (ssid, channel, crypto)

aps = {}
sniff(iface='mon0', prn=insert_ap, store=False, lfilter=lambda p: (Dot11Beacon in p or Dot11ProbeResp in p))
