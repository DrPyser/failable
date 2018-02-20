from itertools import islice
from collections.abc import Sequence

class SeqView(Sequence):
    """Readonly 'view' of a sequence"""
    __slots__ = ["_data", "_slice"]
    
    def __init__(self, data, start=0, stop=None, step=None):
        self._data = data
        self._slice = slice(start, stop or len(self.data), step or 1)

    @property
    def data(self):
        return self._data

    @property
    def slice(self):
        return self._slice

    def __len__(self):
        return len(range(self.slice.start, min(self.slice.stop, len(self._data)), self.slice.step))
    
    def __iter__(self):
        for i in range(self.slice.start, self.slice.stop, self.slice.step):
            yield self.data[i]

    def __getitem__(self, index):
        if type(index) is slice:
            start = self.slice.start + index.start*self.slice.step
            stop = self.slice.start + index.stop*self.slice.step
            step = self.slice.step*(index.step if index.step is not None else 1)
            return SeqView(self.data, start, stop, step)
        elif type(index) is int:
            i = self.slice.start + index*self.slice.step
            if i < self.slice.stop:
                return self.data[i]
            else:
                raise IndexError("ListView index out of range")            

    def __contains__(self, member):
        return any(x == member for x in self)

    def __reversed__(self):
        return SeqView(self._data, self.slice.stop-1, self.slice.start-1, -self.slice.step)
            
    def __repr__(self):
        return "SeqView([{}])".format(
            ",".join(
                str(self.data[i]) for i in range(
                    min(self.slice.start, len(self.data)),
                    min(len(self.data), self.slice.stop),
                    self.slice.step
                )
            )
        )

