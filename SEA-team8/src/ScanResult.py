class Scan_Result:
    def __init__(self, scan_name, run_name, start_time, end_time, ips, exec_status, scan_result, scan_status="", name="", exec_num=""):
        self.scan_name = scan_name
        self.run_name = run_name
        self.start_time = start_time    # datetime
        self.end_time = end_time    # datetime
        self.ip_list = list()
        self.add_ip(ips)  # list
        self.exec_status = exec_status  # success/failure
        self.formatted_output = None

    # add 1 or more ip addresses to ip_list
    def add_ip(self, ip):
        if isinstance(ip, str):  # if 'ip' is just one ip address
            self.ip_list.append(ip)  # add 1 ip to the end
        elif isinstance(ip, list):  # if 'ip' is multiple ip addresses
            self.ip_list.extend(ip)  # extend the current list

    # SETTERS

    def set_start_time(self, time):
        self.start_time = time

    def set_end_time(self, time):
        self.end_time = time

    def set_ip_list(self, ips):
        self.ip_list = ips

    def set_exec_status(self, stat):
        self.exec_status = stat

    def set_formatted_output(self, output):
        self.formatted_output = output

    # GETTERS

    def get_results(self):
        str_ip_list = ", ".join(self.ip_list)
        str_ip_list = str_ip_list.replace('[', '')
        str_ip_list = str_ip_list.replace(']', '')
        str_ip_list = str_ip_list.replace('\'', '')

        return [self.start_time, self.end_time, str_ip_list, self.exec_status]







