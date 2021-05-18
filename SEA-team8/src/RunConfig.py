import Target

class Run_Config:
    def __init__(self, name="", desc="", *target):
        self.name = name    # crc: should be getting from tool config class
        self.desc = desc
        self.state = "configured"  # configured / active / inactive / terminated
        self.target = target    # is a Target object, contains white/blacklist of ip's

    def load_from_db(self, run_name, db):
        run = db.getRun(run_name)
        self.name = run["run_name"]
        self.desc = run["run_description"]

        self.target = Target.Target()
        self.target.add_to_whitelist(run["whitelist"])
        self.target.add_to_blacklist(run["blacklist"])


    # SETTERS

    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.desc = desc

    def set_state(self, state):
        self.state = state

    def set_target(self, target):
        self.target = target

    # GETTERS

    def get_name(self):
        return self.name

    def get_description(self):
        return self.desc

    def get_state(self):
        return self.state

    def get_target(self):
        return self.target

