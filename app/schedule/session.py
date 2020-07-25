class Session:

    def __init__(self):
        self.title = None
        self.start = None
        self.description = None
        self.url = None
        self.speaker = None
        self.img_url = None
        self.calendar_url = None

    def __str__(self):
        return self.title
