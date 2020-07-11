from leaguepedia_sb_parser.parser import Parser


class MultiParser(object):
    start = '{{box|start}}\n'
    between = '\n{{box|break}}\n'
    end = '\n{{box|end}}'
    
    def __init__(self, parser: Parser):
        self.parser = parser
    
    def parse_multi_series(self, text):
        list_of_series = text.split('\n\n')
        output = []
        for series in list_of_series:
            output.append(self.parser.parse_series(series))
        
        return self.start + self.between.join(output) + self.end
