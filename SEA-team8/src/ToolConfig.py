import OutputDataSpec

class Tool_Config:
    def __init__(self, name="", desc="", path="", opt_and_arg="", output_spec=None):
        self.name = name
        self.desc = desc
        self.path = path
        self.opt_and_arg = opt_and_arg
        self.output_spec = output_spec

    def load_from_db(self, tool_name, db):
        tool = db.getTool(tool_name)
        self.name = tool["tool_name"]
        self.desc = tool["tool_description"]
        self.desc = tool["tool_path"]
        self.opt_and_arg = tool["tool_option_and_argument"]
        self.output_spec = tool["tool_output_specification"]

        # ideally get output data from the database using
        # the output data spec class, like so:
        # self.output_spec = OutputDataSpec.Output_Data_Spec()
        # self.output_spec.load_from_db(tool, self.name)

    # SETTERS

    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.desc = desc

    def set_path(self, path):
        self.path = path

    def set_opt_and_arg(self, opt_and_arg):
        self.opt_and_arg = opt_and_arg

    def set_output_spec(self, output_spec):
        self.output_spec = output_spec

    # GETTERS

    def get_name(self):
        return self.name

    def get_desc(self):
        return self.desc

    def get_path(self):
        return self.path

    def get_opt_and_arg(self):
        return self.opt_and_arg

    def get_output_spec(self):
        return self.output_spec





