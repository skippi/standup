from standup import persist

def test_save_load_channels():
    channels = {1, 2, 3, 4}
    persist.save_channels(channels)
    assert persist.load_channels() == channels
