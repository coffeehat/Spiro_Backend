def singleton(cls):
    instances = {}

    def inner():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return inner