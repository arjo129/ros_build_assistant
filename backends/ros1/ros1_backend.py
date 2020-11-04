from rospkg import RosPack
from rosmsg import list_msgs

class Ros1Backend:

    def __init__(self):
        self.rp = RosPack()
        self.all_msgs = []
        self.message_owner = []
        self.headers = []
        self.header_package_mapping = {}

    def get_exported_headers(self):
        if len(self.headers) > 0:
            return self.headers

        messages = self.get_all_messages()
        self.headers += self.messagefiles_to_headers(messages)
        return self.headers
    
    def get_package_from_header(self, header):
        return self.header_package_mapping[header]
        
    def messagefiles_to_headers(self, message):
        headers = [self.messagefile_to_header(x) for x in message]
        
        for _id in range(len(message)):
            self.header_package_mapping[headers[_id]] = self.message_owner[_id]
        return headers

    def messagefile_to_header(self, message):
        return message+".h"

    def get_package_list(self):
        return self.rp.list()

    def get_all_messages(self):

        if len(self.all_msgs) > 0:
            #return from cache
            return self.all_msgs

        for package in self.get_package_list():
            msgs = list_msgs(package, self.rp)
            self.all_msgs += msgs
            self.message_owner += [package] * len(msgs)

        return self.all_msgs