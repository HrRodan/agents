import heapq

class Graph:
    def __init__(self):
        self.edges = {}

    def add_edge(self, u, v, weight):
        if u not in self.edges:
            self.edges[u] = []
        self.edges[u].append((v, weight))

    def dijkstra(self, start):
        min_heap = [(0, start)]  # (cost, node)
        distances = {node: float('inf') for node in self.edges}  # Initialize distances
        distances[start] = 0

        while min_heap:
            current_distance, current_node = heapq.heappop(min_heap)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.edges.get(current_node, []):
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(min_heap, (distance, neighbor))

        return distances

# Example usage:
if __name__ == '__main__':
    g = Graph()
    g.add_edge('A', 'B', 1)
    g.add_edge('A', 'C', 4)
    g.add_edge('B', 'C', 2)
    g.add_edge('B', 'D', 5)
    g.add_edge('C', 'D', 1)

    distances = g.dijkstra('A')
    print('Distances from A:', distances)
