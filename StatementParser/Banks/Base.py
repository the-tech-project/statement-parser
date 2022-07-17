###
# Bank statement parser base class.
###

import json
import os

class Base:

    def __init__(self):
        self.BANK_DETAILS = self.get_mapping()

    def get_mapping(self):
        # Opening JSON file
        file = open(os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), 'mapping.json'))

        # returns JSON object as
        # a dictionary
        data = json.load(file)

        # Closing file
        file.close()

        return data

    def maybe_convert_to_int(self, string):
        if str == type( string ):
            try:
                return int( string )
            except:
                return string
        return string

    def maybe_convert_to_float(self, string):
        if str == type( string ):
            try:
                return float( string.replace(',','') )
            except:
                return string
        return string

    def index_exist(self, a_list, index):
        return index < len(a_list)
