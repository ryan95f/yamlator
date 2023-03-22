import hashlib
from collections import defaultdict


class DependencyManager:
    def __init__(self) -> None:
        self._graph = defaultdict(list)

    def add(self, content: str) -> str:
        md5 = hashlib.md5(content.encode('utf-8'))
        digest = md5.hexdigest()

        self._graph[digest] = []
        return digest

    def add_child(self, parent_hash: str, child_hash: str) -> str:
        self._graph[parent_hash].append(child_hash)

    def has_cycle(self) -> bool:
        visited = defaultdict(bool)
        rec_stack = defaultdict(bool)

        for node in self._graph.keys():
            if not visited[node]:
                if self._detect_cycle(node, visited, rec_stack):
                    return True
        return False

    def _detect_cycle(self, curr_node, visited, rec_stack):
        visited[curr_node] = True
        rec_stack[curr_node] = True

        for child_node in self._graph[curr_node]:
            if not visited[child_node]:
                if self._detect_cycle(child_node, visited, rec_stack):
                    return True
            elif rec_stack[child_node]:
                return True

        rec_stack[curr_node] = False
        return False
