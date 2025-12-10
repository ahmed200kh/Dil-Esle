class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current = None

    def add(self, name, screen):
        self.screens[name] = screen

    def switch(self, name):
        self.current = self.screens.get(name)
