# SRS 33: Each XML report shall comprise of at least one run result
class Xml_Report:
    def __init__(self, name, desc, content):
        self.name = name
        self.desc = desc
        self.content = content
        # self.file_path = file_path

    # def load_from_db(self, xml_name, db):
    #     # xml_report = db.get_xml_report(xml_name)
    #     # self.name = xml_report["xml_name"]
    #     # self.desc = xml_report["xml_description"]
    #     # store file path in db?

    # SETTERS

    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.desc = desc

    def set_content(self, content):
        self.content = content

    # def set_file_path(self, fp):
    #     self.file_path = fp

    # GETTERS

    def get_name(self):
        return self.name

    def get_desc(self):
        return self.desc

    def get_content(self):
        return  self.content

    # def get_file_path(self):
    #     return self.file_path


