class InnPropertyData:
    def __init__(self, property_data):
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
