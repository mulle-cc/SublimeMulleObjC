#
# This is for development outside of Sublime Text when
# import sublime_plugin doesn't work
#
class TextCommand:
    def __init__(self, view, *args, **kwargs):
        self.view = view
        self.args = args
        self.kwargs = kwargs

    def is_enabled(self):
      return True