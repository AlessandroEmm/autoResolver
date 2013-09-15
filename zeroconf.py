import select
import sys
import pybonjour
import threading
import requests


class zeroconf(threading.Thread):
    """docstring for ClassName"""
    def __init__(self, resolvedPeers, publishPort, regType, name, onlyCollect=False):
        super().__init__()
        self.resolvedPeers = resolvedPeers
        self.resolved = []
        self.port = publishPort
        self.regType = regType
        self.name = name
        self.timeout  = 5
        self.domain = "local"


    def register_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print('Registered service:')
            print ('  name    =', self.name)
            print ('  regtype =', self.regType)
            print ('  domain  =', self.domain)


    def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
                         hosttarget, port, txtRecord):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print('Resolved service:')
            print('  fullname   =', fullname)
            print('  hosttarget =', hosttarget)
            print('  port       =', port)
            self.resolved.append(True)
            print("URL  " + "http://" + hosttarget + ":" + str(port) +  "/contract")
            self.resolvedPeers.append({"name": fullname, "host": hosttarget, "port": port })
            try:
                r = requests.get("http://" + hosttarget + ":" + str(port)  +  "/contract")
            except:
                print("HTTP Error!")
                return
            


    def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
                        regtype, replyDomain):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print('Service removed')
            return

        print('Service added; resolving')


        resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                    interfaceIndex,
                                                    serviceName,
                                                    regtype,
                                                    replyDomain,
                                                    self.resolve_callback)
        try:
            while not self.resolved:
                ready = select.select([resolve_sdRef], [], [], self.timeout)
                if resolve_sdRef not in ready[0]:
                    break
                pybonjour.DNSServiceProcessResult(resolve_sdRef)
            else:
                self.resolved.pop()
        finally:
            resolve_sdRef.close()


    def run(self):
        browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regType,
                                              callBack = self.browse_callback)

        sdRef = pybonjour.DNSServiceRegister(name = self.name,
                                         regtype = self.regType,
                                         port = self.port,
                                         callBack = self.register_callback)
        try:
            try:
                while True:
                    ready = select.select([browse_sdRef, sdRef], [], [])
                    if browse_sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(browse_sdRef)
                    if sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(sdRef)
            except KeyboardInterrupt:
                pass
        finally:
            browse_sdRef.close()
            sdRef.close()



    