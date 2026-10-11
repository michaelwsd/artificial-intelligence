import heapq 

graph = {
    'Arad': [('Zerind', 75), ('Sibiu', 140), ('Timisoara', 118)],
    'Zerind': [('Arad', 75), ('Oradea', 71)],
    'Oradea': [('Sibiu', 151), ('Zerind', 71)],
    'Timisoara': [('Arad', 118), ('Lugoj', 111)],
    'Lugoj': [('Mehadia', 70), ('Timisoara', 111)],
    'Mehadia': [('Drobeta', 75), ('Lugoj', 70)],
    'Drobeta': [('Craiova', 120), ('Mehadia', 75)],
    'Craiova': [('Pitesti', 138), ('Rimnicu Vilcea', 146), ('Drobeta', 120)],
    'Sibiu': [('Rimnicu Vilcea', 80), ('Fagaras', 99), ('Oradea', 151), ('Arad', 140)],
    'Rimnicu Vilcea': [('Craiova', 146), ('Pitesti', 97), ('Sibiu', 80)],
    'Pitesti': [('Bucharest', 101), ('Craiova', 138), ('Rimnicu Vilcea', 97)],
    'Fagaras': [('Bucharest', 211), ('Sibiu', 99)],
    'Bucharest': [('Urziceni', 85), ('Giurgiu', 90), ('Pitesti', 101), ('Fagaras', 211)],
    'Giurgiu': [('Bucharest', 90)],
    'Urziceni': [('Vaslui', 142), ('Hirsova', 98), ('Bucharest', 85)],
    'Hirsova': [('Eforie', 86), ('Urziceni', 98)],
    'Eforie': [('Hirsova', 86)],
    'Vaslui': [('Iasi', 92), ('Urziceni', 142)],
    'Iasi': [('Neamt', 87), ('Vaslui', 92)],
    'Neamt': [('Iasi', 87)]
}

def h_function(current):
    if current == 'Arad': return 366
    if current == 'Bucharest': return 0
    if current == 'Craiova': return 160
    if current == 'Drobeta': return 242
    if current == 'Eforie': return 161
    if current == 'Fagaras': return 178
    if current == 'Giurgiu': return 77
    if current == 'Hirsova': return 151
    if current == 'Iasi': return 226
    if current == 'Lugoj': return 244
    if current == 'Mehadia': return 241
    if current == 'Neamt': return 234
    if current == 'Oradea': return 380
    if current == 'Pitesti': return 98
    if current == 'Rimnicu Vilcea': return 193
    if current == 'Sibiu': return 253
    if current == 'Timisoara': return 329
    if current == 'Urziceni': return 80
    if current == 'Vaslui': return 199
    if current == 'Zerind': return 374
    assert False, f'Current state {current} is invalid'

def astar_find_path(src, dst):
    start = (h_function(src), src)
    heap = [start]
    visited = set()
    parent = {src: None}
    costs = {src: 0}

    while heap:
        _, city = heapq.heappop(heap) 

        if city == dst:
            return reconstruct_path(parent, dst)

        if city in visited:
            continue 

        visited.add(city)
        cost = costs[city] # cost to get to this city

        for nei, d in graph[city]:
            if nei in visited:
                continue 

            newd = cost + d # update cost 

            if nei not in costs or newd < costs[nei]:
                costs[nei] = newd 
                parent[nei] = city 
                heapq.heappush(heap, (newd + h_function(nei), nei))
        
    return None

def reconstruct_path(parent, dst):
    path = [dst]
    while parent[dst] is not None:
        path.append(parent[dst])
        dst = parent[dst]

    return path[::-1]

if __name__ == "__main__":
    print(astar_find_path('Arad', 'Bucharest'))