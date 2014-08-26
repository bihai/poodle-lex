import os.path
import json
from ..CoverageSet import CoverageSet

class UnicodeQuery(object):
    _instance = {}
    _db_binary = "BinaryProperties.json"
    _db_property = "Property{code}.json"
    _db_property_aliases = "AliasesProperties.json"
    _db_value_aliases = "AliasesValues.json"
    _db_category = {
        'l': ['lu', 'll', 'lt', 'lm', 'lo'],
        'm': ['mn', 'mc', 'me'],
        'n': ['nd', 'nl', 'no'],
        'p': ['pc', 'pd', 'ps', 'pe', 'pi', 'pf', 'po'],
        's': ['sm', 'sc', 'sk', 'so'],
        'z': ['zs', 'zl', 'zp'],
        'c': ['cc', 'cf', 'cs', 'co', 'cn']
    }
    _db_binary_names = [
        u'ahex', u'alpha', u'bidic', u'bidim', u'cased', u'ce', u'ci', u'compex', 
        u'cwcf', u'cwcm', u'cwkcf', u'cwl', u'cwt', u'cwu', u'dash', u'dep', u'di', 
        u'dia', u'ext', u'grbase', u'grext', u'grlink', u'hex', u'hyphen', u'idc', 
        u'ideo', u'ids', u'idsb', u'idst', u'joinc', u'loe', u'lower', u'math', 
        u'nchar', u'nfdqc', u'nfkdqc', u'oalpha', u'odi', u'ogrext', u'oidc', 
        u'oids', u'olower', u'omath', u'oupper', u'patsyn', u'patws', u'qmark', 
        u'radical', u'sd', u'sterm', u'term', u'uideo', u'upper', u'vs', u'wspace', 
        u'xidc', u'xids', u'xonfc', u'xonfd', u'xonfkc', u'xonfkd'
    ]
    
    @classmethod
    def instance(cls, path):
        """
        @returns: a singleton instance of the UnicodeQuery class
        @param path: the directory containing the JSON copy of the UCD
        """
        realpath = os.path.realpath(path)
        if realpath not in cls._instance:
            cls._instance[realpath] = cls(realpath)
        return cls._instance[realpath]
    
    def __init__(self, path):
        """
        @param path: the directory containing the JSON copy of the UCD
        """
        self.path = path
        self.cache = {}
        
    def get_property(self, property, value=None):
        """
        Retrieves a CoverageSet of every character matching the property
        @param property: the name of the property to look up
        @param value: if the property is non-binary, the value of the property to filter by
        """
        code = self.get_property_code(property)
        if value is not None:
            value = self.get_value_code(code, value)
        if code in self._db_binary_names:
            return self.get_binary_property(code)
        else:
            return self.get_string_property(code, value)
        
    def get_binary_property(self, code):
        """
        Retrieves a CoverageSet of every character matching a binary property
        @param code: The shorthand abbreviation for the property to look up
        @returns a CoverageSet containing every character for which the property is True.
        """
        if self._db_binary not in self.cache:
            with open(os.path.join(self.path, self._db_binary), 'r') as f:
                self.cache[self._db_binary] = json.load(f)
        cache = self.cache[self._db_binary]
        if code not in cache:
            raise ValueError("Code '{code}' not found".format(code=code))
        return CoverageSet(cache[code])
        
    def get_string_property(self, code, value):
        """
        Retrieves characters for which a non-binary property has a certain value
        @param code: The shorthand abbreviation for the property to look up
        @param value: The value which matching codepoints must have for the property
        """
        code_file = self._db_property.format(code=code)
        code_path = os.path.join(self.path, code_file)
        if code_path not in self.cache:
            if not os.path.exists(code_path):
                raise ValueError("Code '{code}' not found").format(code=code)
            with open(code_path, 'r')as f:  
                self.cache[code_path] = json.load(f)
        cache = self.cache[code_path]
        value_code = self.get_value_code(code, value)
        if code == 'gc' and len(value_code) == 1 and value_code in self._db_category:
            # 1st-level categories are just combinations of finer-grained categories
            return CoverageSet.union(*[self.get_string_property(code, i) for i in self._db_category[value_code]])
        if value_code not in cache:
            return CoverageSet()
        else:
            return CoverageSet(cache[value_code])
            
    def get_property_code(self, property):
        """
        Given a property's full name or abbreviated name, return its abbreviated name
        @param property: The name or abbreviation of the property
        @return: string containing the abbreviation to use, sanitized
        """
        property_path = os.path.join(self.path, self._db_property_aliases)
        if property_path not in self.cache:
            with open(property_path, 'r') as f:
                self.cache[property_path] = json.load(f)
        sanitized_property = self.sanitize_input(property)
        if sanitized_property not in self.cache[property_path]:
            return property
        return self.cache[property_path][sanitized_property]
        
    def get_value_code(self, property_code, value):
        """
        Given an enumerated property value's full name or abbreviated name, gets the abbreviated name
        @param property_code: the abbreviated name of the property
        @param value: the full or abbreviated property value to look up
        """
        value_path = os.path.join(self.path, self._db_value_aliases)
        if value_path not in self.cache:
            with open(value_path, 'r') as f:
                self.cache[value_path] = json.load(f)
        code_sanitized = self.sanitize_input(property_code)
        if code_sanitized not in self.cache[value_path]:
            return value
        value_sanitized = self.sanitize_input(value)
        if value_sanitized not in self.cache[value_path][code_sanitized]:
            return value
        return self.cache[value_path][code_sanitized][value_sanitized]
        
    @staticmethod
    def sanitize_input(input):
        """
        Reduce unicode property names and values 
        @param input: the text to sanitize
        @return: string containing the sanitized input
        """
        return input.lower().replace('_', '').replace('-', '').replace(' ', '')
        
    @staticmethod
    def is_binary(code): 
        """
        
        """
        return code.lower() in [
            ]
            
    @staticmethod
    def category_combines(code):
        return 
        