class ApibeanSpace():
    def __init__(self, profile="main"):
        self._profile = profile
        self._globals = dict()
        self._storage = dict()

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    def globals(self, **kwargs):
        self._globals.update(**kwargs)

    def update(self, **kwargs):
        if self._profile not in self._storage:
            self._storage[self._profile] = dict()
        self._storage[self._profile].update(**kwargs)

    def __getitem__(self, key):
        if self._profile not in self._storage:
            self._storage[self._profile] = dict()
        return self._storage[self._profile].get(key, self._globals.get(key, None))

    def __setitem__(self, key, value):
        if self._profile not in self._storage:
            self._storage[self._profile] = dict()
        self._storage[self._profile][key] = value

    def __delitem__(self, key):
        if key in self._storage[self._profile]:
            del self._storage[self._profile][key]
