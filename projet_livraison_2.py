from random import randint

def set_world(N, file):
    world = {"map": [["." for i in range(N)] for j in range(N)], "graph": {}, "obs": 0, "drone": [0, []]}
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            entity, coordinates = line.split(' : ')

            if entity == 'D':
                i, j = map(int, coordinates.strip()[1:-1].split(','))
                world["map"][i][j] = 'D'
                world["drone"][0] += 1
                world["drone"][1].append([i, j])
            elif entity.isdigit():
                i, j = map(int, coordinates.strip()[1:-1].split(','))
                world["map"][i][j] = entity
                world["graph"][int(entity)] = [] 
            elif entity == 'X':
                world["obs"] = 1
                c1, c2 = coordinates.split('; ')
                i1, j1 = map(int, c1.strip()[1:-1].split(','))
                i2, j2 = map(int, c2.strip()[1:-1].split(','))
                imin = min(i1, i2)
                imax = max(i1, i2)
                jmin = min(j1, j2)
                jmax = max(j1, j2)
                for i in range(imin, imax+1):
                    for j in range(jmin, jmax+1):
                        world["map"][i][j] = 'X'
            elif entity == 'E':
                v1, v2 = map(int, coordinates.strip()[1:-1].split(','))
                cv1 = get_village_coords(world["map"], v1)
                cv2 = get_village_coords(world["map"], v2)
                path, distance = dijkstra(world["map"], cv1, cv2)
                world["graph"][v1].append([v2, distance])
                world["graph"][v2].append([v1, distance])
                for i, j in path:
                    if world["map"][i][j] == '.':
                        world["map"][i][j] = "•"
            else:
                continue
    return world

def dijkstra(map, start, end):
    N = len(map)
    distances = [[float('inf') for j in range(N)] for i in range(N)]
    distances[start[0]][start[1]] = 0
    visited = [[False for j in range(N)] for i in range(N)]
    predecessors = [[None for j in range(N)] for i in range(N)]
    queue = [start]
    while queue:
        i, j = queue.pop(0)
        if visited[i][j]:
            continue
        visited[i][j] = True
        if [i, j] == end:
            break
        for di, dj in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            ni, nj = i + di, j + dj
            if 0 <= ni < N and 0 <= nj < N and not visited[ni][nj] and map[ni][nj] != 'X':
                new_distance = distances[i][j] + 1
                if new_distance < distances[ni][nj]:
                    distances[ni][nj] = new_distance
                    predecessors[ni][nj] = [i, j]
                    queue.append([ni, nj])
    path = []
    [i, j] = end
    while predecessors[i][j] is not None:
        path.append([i, j])
        [i, j] = predecessors[i][j]
    path.reverse()
    return path, distances[end[0]][end[1]]

def get_village_coords(map, village_num):
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == str(village_num):
                return [i, j]
    return None

def set_graph(world):
    for v1 in world["graph"]:
        for v2 in world["graph"]:
            if v1 < v2:
                cv1 = get_village_coords(world["map"], v1)
                cv2 = get_village_coords(world["map"], v2)
                path, distance = dijkstra(world["map"], cv1, cv2)
                world["graph"][v1].append([v2, distance])
                world["graph"][v2].append([v1, distance])

def init_random_drone_pos(graph, K, drone_pos):
    N = len(graph)
    k = K
    occuped_villages = []
    while (k > 0 and (0 in drone_pos)):
        i = randint(0, N-1)
        if drone_pos[i] != 1:
            drone_pos[i] = 1
            k -= 1

def get_nearest_village(villages):
    v = 0
    d = villages[0]
    for i in range(1, len(villages)):
        if villages[i] < d:
            v = i
            d = villages[i]
    return v, d

def init_drone_pos(map, graph, drone, drone_pos):
    for cd in drone[1]:
        villages = [float('inf') for i in range(len(graph))]
        for v in graph:
            cv = get_village_coords(map, v)
            path, distance = dijkstra(map, cd, cv)
            villages[v-1] = distance
        
        nearest_village, d = get_nearest_village(villages)

        drone_pos[nearest_village] = 1 + d

def compute_optimal_neighboor(village, graph, visited, drone_pos):
    next_village = village
    distance = float('inf')
    distance2 = float('inf')
    for neighboor in graph[village]:
        if neighboor[1] < distance and visited[neighboor[0]-1] != 2:
            distance = neighboor[1]
            distance2 = neighboor[1]
            next_village = neighboor[0]
        elif distance == float('inf') and visited[neighboor[0]-1] == 2:
            distance2 = neighboor[1]
            next_village = neighboor[0]
    
    if (distance != distance2):
        distance = distance2
    
    if drone_pos[next_village-1] > 1:
        next_village = village
        distance = 0

    print("Drone du village ", village, " va sur le village ", next_village, " à une distance de ", distance)
    return next_village, distance

def optimal_move_drone(graph, drone_pos, visited, t, time):
    N = len(graph)
    new_drone_pos = [0 for i in range(N)]
    for i in range(len(drone_pos)):
        if drone_pos[i] == 1:
            next_village, distance = compute_optimal_neighboor(i+1, graph, visited, drone_pos)
            #if drone_pos[next_village-1] <= 1:
            new_drone_pos[next_village-1] = 1 + distance

            if visited[next_village-1] == 0:
                visited[next_village-1] = 1
                t[next_village-1] = time
            elif visited[next_village-1] == 1:
                visited[next_village-1] = 2
                t[next_village-1] = time+distance - t[next_village-1]
            else:
                continue
            
            #else:
                #new_drone_pos[next_village-1] = drone_pos[next_village-1] - 1
            
        elif drone_pos[i] > 1 :
            new_drone_pos[i] = drone_pos[i] - 1
        else:
            continue

    return new_drone_pos


def optimal_path(map, graph, K, drone):
    '''graph: graph's world, K: number of drones'''
    N = len(graph)
    visited = [0 for i in range(N)]
    t = [0 for i in range(N)]
    drone_pos = [0 for i in range(N)]
    
    if drone[0] == 0:
        init_random_drone_pos(graph, K, drone_pos)
    else:
        init_drone_pos(map, graph, drone, drone_pos)

    for i in range(len(drone_pos)):
        if drone_pos[i] >= 1:
            visited[i] = 1
    
    time = 0
    while ((0 in visited) or (1 in visited)):
        print("Temps ", time)
        print("Drones positions: ", drone_pos)
        print("Villages visités: ", visited)
        drone_pos = optimal_move_drone(graph, drone_pos, visited, t, time)
        time += 1

    for i in range(len(drone_pos)):
        if drone_pos[i] != 0:
            t[i] += drone_pos[i]

    print("Temps ", time)
    print("Drones positions: ", drone_pos)
    print("Villages visités: ", visited)
    return t


def world_display(map):
    print("==== MAP DISPLAY ====")
    N = len(map)
    for i in range(N):
        line = ""
        for j in range(N):
            line += map[i][j]
        print(line)

def graph_display(graph):
    print("==== GRAPH DISPLAY ====")
    for key in graph:
        for neighboor in graph[key]:
            print(key, "-", neighboor[1], "->", neighboor[0])

def obs_display(obs):
    print("==== OBS DISPLAY ====")
    if obs == 0:
        print("Désactivé")
    else:
        print("Activé")

world = set_world(50, "village1.txt")
if world["obs"] == 0:
    set_graph(world)

world_display(world["map"])
graph_display(world["graph"])
obs_display(world["obs"])

print(optimal_path(world["map"], world["graph"], 3, world["drone"]))