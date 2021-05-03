class EventCannotBeLocated(KeyError):
    def __str__(self):
        return "The name of the page that this match history is supposed to give cannot be located!"
