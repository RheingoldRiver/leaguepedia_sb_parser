from leaguepedia_sb_parser.parser import Parser


class MultiParser(object):
    between = '\n{{box|break}}\n'
    
    def __init__(self, parser: Parser, wrap_in_box=False):
        self.start = ''
        self.end = ''
        if wrap_in_box:
            self.start = '{{box|start}}\n'
            self.end = '\n{{box|end}}'
        self.parser = parser
    
    def parse_multi_series(self, text):
        list_of_series = text.split('\n\n')
        output = []
        for series in list_of_series:
            series_array = series.split('\n')
            output.append(self.parser.parse_series(series_array))
        
        return self.start + self.between.join(output) + self.end
