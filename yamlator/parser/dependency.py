"""Utilties for managing dependencies in Yamlator"""

import copy
import hashlib
from collections import defaultdict


class DependencyManager:
    """Tracks and detects dependencies between objects by representing
    data as a Md5 hash. Once a node has been added, a depth first search
    is executed against all nodes to detect a cycle
    """

    def __init__(self) -> None:
        self._graph = {}

    @property
    def graph(self) -> dict:
        return copy.deepcopy(self._graph)

    def add(self, node: str) -> str:
        """Add a new node to the graph. The contents of the parameter
        `node` will be hashed with Md5

        Args:
            node (str): A string that contains the content or represents
                an item that needs to be tracked for a cycle

        Return:
            A Md5 hash of the content provided in the `node` parameter
        """
        md5 = hashlib.md5(node.encode('utf-8'))
        digest = md5.hexdigest()

        self._graph[digest] = []
        return digest

    def add_child(self, parent_hash: str, child_hash: str) -> bool:
        """Adds a child node to a parent node in the dependency chain

        Args:
            parent_hash (str): The Md5 hash of the parent node
            child_hash (str): The Md5 hash of the child node

        Returns:
            True to indicate that the function completed successfully
        """
        if not self._graph.get(parent_hash):
            self._graph[parent_hash] = []

        self._graph[parent_hash].append(child_hash)
        return True

    def has_cycle(self) -> bool:
        """Detects a cycle against the contents the manager is representing

        Returns:
            A boolean to indicate if a cycle is present. True indicates
            a cycle was detected, False indicates no cycle is present
        """
        visited = defaultdict(bool)
        rec_stack = defaultdict(bool)

        for node in self._graph:
            if not visited[node]:
                if self._detect_cycle(node, visited, rec_stack):
                    return True
        return False

    def _detect_cycle(self, curr_node: str, visited: dict,
                      rec_stack: dict) -> bool:
        visited[curr_node] = True
        rec_stack[curr_node] = True

        parent_node = self._graph.get(curr_node, [])
        for child_node in parent_node:
            if not visited[child_node]:
                if self._detect_cycle(child_node, visited, rec_stack):
                    return True
            elif rec_stack[child_node]:
                return True

        rec_stack[curr_node] = False
        return False
