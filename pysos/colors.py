class Color:

    def __init__(self):
        self.colors = {}
        self.colors['BOLD'] = '\033[1m'
        self.colors['HEADER'] = '\033[95m'
        self.colors['BHEADER'] = self.colors['HEADER'] + self.colors['BOLD']
        self.colors['BLUE'] = '\033[94m'
        self.colors['BBLUE'] = self.colors['BLUE'] + self.colors['BOLD']
        self.colors['GREEN'] = '\033[92m'
        self.colors['BGREEN'] = self.colors['GREEN'] + self.colors['BOLD']
        self.colors['SECTION'] = '\033[93m'
        self.colors['BSECTION'] = self.colors['SECTION'] + self.colors['BOLD']
        self.colors['RED'] = '\033[91m'
        self.colors['BRED'] = self.colors['RED'] + self.colors['BOLD']
        self.colors['ENDC'] = '\033[0m'
        self.colors['WHITE'] = '\033[1;37m'
        self.colors['GREY'] = '\033[37m'
        self.colors['WARN'] = '\033[33m'
        self.colors['PURPLE'] = '\033[35m'
        self.colors['BPURPLE'] = self.colors['PURPLE'] + self.colors['BOLD']
        self.colors['CYAN'] = '\033[36m'
        self.colors['DBLUE'] = '\033[34m'
        for k, v in self.colors.items():
            self.__dict__[k] = v

    def fmt(self, color, text):
        return color + text[0] + self.colors['ENDC'] + ' ' + ' '.join(text[1:])

    def __getattr__(self, name):
        def trapit(*args):
            if name.upper() not in list(self.colors.keys()):
                color = 'endc'
            else:
                color = name
            if not args:
                return
            print(self.fmt(self.colors[color.upper()], args))
        return trapit
