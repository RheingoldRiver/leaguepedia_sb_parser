from leaguepedia_sb_parser.parser import Parser


class MultiParser(object):
    between = '\n{{box|break}}\n'
    
    def __init__(self, parser: Parser, wrap_in_box=False):
        self.end = ''
        self.start = ''
        if wrap_in_box:
            self.end = '\n{{box|end}}'
            self.start = '{{box|start}}\n'
        self.parser = parser
    
    def parse_multi_series(self, text):
        list_of_series = text.split('\n\n')
        output = []
        for series in list_of_series:
            output.append(self.parser.parse_series(series))
        
        return self.start + self.between.join(output) + self.end
