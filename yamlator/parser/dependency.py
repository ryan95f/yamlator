import hashlib
from collections import defaultdict


class DependencyManager:
    def __init__(self) -> None:
        self._graph = defaultdict(list)
        self.vertices = {}
        self.lu = []

    def add(self, curr: str) -> str:
        self.vertices[curr] = len(self)
        self.lu.append(curr)
        self._graph[curr] = []
        return curr
        # md5 = hashlib.md5(curr.encode('utf-8'))
        # md5_digest = md5.hexdigest()
        # self._graph[md5_digest] = []
        # return md5_digest

    def add_child(self, parent: str, content: str) -> str:
        self._graph[parent].append(content)

        # md5 = hashlib.md5(content.encode('utf-8'))
        # md5_digest = md5.hexdigest()

        # self._graph[parent].append(md5_digest)
        # return md5_digest

    def hash_cycle(self, parent: str) -> bool:
        visited = [False] * (len(self.vertices) + 1)
        rec_stack = [False] * (len(self.vertices) + 1)

        for node in range(len(self.vertices)):
            if not visited[node]:
                if self._detect_cycle(node, visited, rec_stack):
                    return True
        return False

    def _detect_cycle(self, v, visited, rec_stack):
        visited[v] = True
        rec_stack[v] = True

        k = self.lu[v]
        for n in self._graph[k]:
            t = self.vertices[n]

            if not visited[t]:
                if self._detect_cycle(t, visited, rec_stack):
                    return True
            elif rec_stack[t]:
                return True

        rec_stack[v] = False
        return False

    def __len__(self) -> int:
        return len(self._graph)
