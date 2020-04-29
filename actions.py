import weakref

class Action:
    def __init__(self, fn, parent, once = False):
        self._fn = fn
        self._parent = weakref.ref(parent)
        self._once = once
        self._count = 0

    def __call__(self, *args, **kwargs):
        r = self._fn(*args)
        self._count += 1
        if self.once:
            print("Need to remove once only action")
        return r

class ActionContainer:
    def __init__(self):
        self._actions = []
        self._blocked = 0
        self._queued = []

    @property
    def actions(self):
        return self._actions

    def block(self):
        self._blocked += 1

    def unblock(self):
        self._blocked -= 1

    def __call__(self, *args, **kwargs):

        self._blocked += 1
        for act in self._actions:
            if type(act) == weakref.ref:
                wact = act
                act = wact()
                if act is None:
                    # print("Need to remove dead weak ref")
                    pass
            if act is not None:
                act(*args, **kwargs)
        self._blocked -= 1

        self.clean()

    def clean(self):
        if not self._blocked:
            if self._queued:
                print(f"{len(self._queued)} queued items")
                for q in self._queued:
                    if type(q) == weakref.ref:
                        wact = q
                        q = wact()
                    if q is not None:
                        q()
                if not self._queued:
                    print("Queue cleared")

    def add(self, func, weak=True, once=False):
        if self._blocked: # Avoid modifiying the list while it's being iterated
            if isinstance(func, Action):
                act = func
            else:
                act = Action(func, self)
            act.once = once
            _act = weakref.ref(act) if weak else act
            self._queued.append(lambda act=_act: self._actions.append(act))
            return act

        act = Action(func, self)
        act.once = once
        _act = weakref.ref(act) if weak else act
        self._actions.append(_act)
        return act

    def remove(self, func):
        print("Need to implement remove action from container")