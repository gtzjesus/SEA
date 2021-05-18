class Target:
    def __init__(self):
        self.whitelist = []
        self.blacklist = []

    # Add an ip address or list of ip addresses to the current whitelist
    def add_to_whitelist(self, ip):
        if isinstance(ip, str): # if 'ip' is just one ip address
            self.whitelist.append(ip)   # add 1 ip to the end
        elif isinstance(ip, list):  # if 'ip' is multiple ip addresses
            self.whitelist.extend(ip)   # extend the current whitelist

    # Add an ip address or list of ip addresses to the current blacklist
    def add_to_blacklist(self, ip):
        if isinstance(ip, str):  # if 'ip' is just one ip address
            self.whitelist.append(ip)  # add 1 ip to the end
        elif isinstance(ip, list):  # if 'ip' is multiple ip addresses
            self.whitelist.extend(ip)  # extend the current blacklist

    # GETTERS

    def get_whitelist(self):
        wl_str = " "
        return wl_str.join(self.whitelist)

    def get_blacklist(self):
        bl_str = " "
        return bl_str.join(self.blacklist)
