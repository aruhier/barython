
def disable_spawn_bar(obj):
    """
    Disable write_in_bar and init_bar
    """
    def mock_write_in_bar(self, *args, **kwargs):
        """
        Just here to raise AttributeError if self._bar doesn't exist
        """
        if not getattr(self, "_bar", None):
            raise AttributeError

    def mock_init_bar(self, *args, **kwargs):
        """
        Just here to raise AttributeError if self._bar doesn't exist
        """
        self._bar = True

    obj.init_bar = mock_init_bar
    obj._write_in_bar = mock_write_in_bar
