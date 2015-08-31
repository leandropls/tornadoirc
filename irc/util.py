# coding: utf-8

# setitem, getitem, contains, get, has_key, pop, setdefault, and update.
class LowerCaseDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self:
            lc = key.lower()
            if key != lc:
                super().__setitem__(lc, super().__getitem__(key))
                super().__delitem__(key)

    def __contains__(self, key, *args, **kwargs):
        return super().__contains__(key.lower(), *args, **kwargs)

    def __delitem__(self, key, *args, **kwargs):
        return super().__delitem__(key.lower(), *args, **kwargs)

    def __getitem__(self, key, *args, **kwargs):
        return super().__getitem__(key.lower(), *args, **kwargs)

    def __setitem__(self, key, *args, **kwargs):
        super().__setitem__(key.lower(), *args, **kwargs)

    def fromkeys(self, iterable, *args, **kwargs):
        iterable = (x.lower() for x in iterable)
        return super().fromkeys(iterable, *args, **kwargs)

    def get(self, k, *args, **kwargs):
        return super().get(k.lower(), *args, **kwargs)

    def pop(self, k, *args, **kwargs):
        return super().pop(k.lower(), *args, **kwargs)

    def setdefault(self, k, *args, **kwargs):
        return super().setdefault(k.lower(), *args, **kwargs)

    def update(self, E = None, **F):
        if E:
            if hasattr(E, 'keys'):
                for k in E:
                    self[k] = E[k]
            else:
                for k, v in E:
                    self[k] = v
        for k in F:
            self[k] = F[k]
