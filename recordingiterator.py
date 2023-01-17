class RecordingIterator:
    def __init__(self, recordings: list[str]) -> None:
        self.recordings = recordings
        self.state = 0
        self.n = len(recordings)

    def forward(self) -> None:
        if self.state + 1 < self.n:
            self.state += 1
        else:
            self.state = 0

    def backward(self) -> None:
        if 0 < self.state:
            self.state -= 1
        else:
            self.state = self.n - 1

    def get_rec(self) -> str:
        return self.recordings[self.state]

    def get_next(self) -> str:
        self.forward()
        return self.get_rec()

    def get_prev(self) -> str:
        self.backward()
        return self.get_rec()
