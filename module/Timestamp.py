class Timestamp:
    def __init__(self,start = 0.0, end = 0.0, word='word', isInclude=False,feature=None, label=None):
        self.start = start
        self.end = end
        self.word = word
        self.isInclude = isInclude
        self.feature = feature
        self.label = label
        
    def get_duration(self):
        return self.end - self.start