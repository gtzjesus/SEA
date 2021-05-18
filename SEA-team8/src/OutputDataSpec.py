class Output_Data_Spec:
    def __init__(self, data_type="", data_val=""):
        self.data_type = data_type
        self.data_val = data_val

    # def load_from_db(self, tool, tool_name)

    # SETTERS

    def set_data_type(self, d_type):
        self.data_type = d_type

    def set_data_val(self, d_val):
        self.data_val = d_val

    # GETTERS

    def get_data_type(self):
        return self.data_type

    def get_data_value(self):
        return self.data_val

