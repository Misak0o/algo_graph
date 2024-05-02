def read_graph(N, nom_fichier):
    graphe = {'villages': {}, 'obstacles': [], 'drones': {}, 'entites': {}}
    ordered_villages = []
    acc = 1
    with open(nom_fichier, 'r') as f:
        for ligne in f:
            ligne = ligne.strip()
            entite, coordonnees = ligne.split(' : ')

            if entite == 'D':
                x, y = map(int, coordonnees.strip()[1:-1].split(','))
                graphe['drones'][acc] = (x,y)
                acc = acc + 1
            elif entite.isdigit():
                identite = int(entite)
                x, y = map(int, coordonnees.strip()[1:-1].split(','))
                if 0 <= x <= N and 0 <= y <= N:  # Vérification des coordonnées valides
                    graphe['villages'][identite] = (x, y)
                    ordered_villages.append((x, y))
                else:
                    print(f"Attention: Les coordonnées du village {identite} ne sont pas valides.")
            elif entite == 'X':
                obstacles = [tuple(map(int, p.strip()[1:-1].split(','))) for p in coordonnees.split(';')]
                graphe['obstacles'].extend(obstacles)
            elif entite == 'E':
                entite_coordonnees = [tuple(coord.strip()[1:-1].split(',')) for coord in coordonnees.split(';')]
                if entite in graphe['entites']:
                    graphe['entites'][entite].extend(entite_coordonnees)
                else:
                    graphe['entites'][entite] = entite_coordonnees

    graphe['ordered_villages'] = ordered_villages
    return graphe



def a_star_search(graph, heuristic):
    initial_state = {
        'drone_positions': list(graph['drones'].values()),
        'remaining_villages': list(graph['villages'].values()),
        'path': [],
        'g_score': 0,
        'h_score': heuristic(list(graph['drones'].values())[0], list(graph['villages'].values())[-1]),
        'f_score': heuristic(list(graph['drones'].values())[0], list(graph['villages'].values())[-1]),
        'hash': (tuple(graph['drones'].values()),) + tuple(graph['villages'].values())
    }

    open_list = [initial_state]
    closed_set = set()

    while open_list:
        current_state = min(open_list, key=lambda x: x['f_score'])
        open_list.remove(current_state)

        if current_state['remaining_villages'] == []:
            return current_state['path']

        closed_set.add(current_state['hash'])

        for successor in generate_successors(current_state, graph):
            if successor['hash'] in closed_set:
                continue

            if successor not in open_list:
                open_list.append(successor)
            else:
                existing_index = open_list.index(successor)
                existing_successor = open_list[existing_index]
                if successor['g_score'] < existing_successor['g_score']:
                    open_list[existing_index] = successor

    return None


def generate_successors(state, graph):
    successors = []

    for drone_position in state['drone_positions']:
        for village in state['remaining_villages']:
            new_drone_positions = state['drone_positions'][:]
            new_drone_positions[new_drone_positions.index(drone_position)] = village

            new_remaining_villages = state['remaining_villages'][:]
            new_remaining_villages.remove(village)

            new_state = {
                'drone_positions': new_drone_positions,
                'remaining_villages': new_remaining_villages,
                'path': state['path'] + [(drone_position, village)],
                'g_score': state['g_score'] + distance(drone_position, village),
                'h_score': heuristic(village, new_remaining_villages[-1]) if new_remaining_villages else 0,
                'f_score': state['g_score'] + distance(drone_position, village) + heuristic(village, new_remaining_villages[-1]) if new_remaining_villages else 0,
                'hash': tuple(new_drone_positions + new_remaining_villages)
            }

            successors.append(new_state)

    return successors


def heuristic(village1, village2):
    return abs(village1[0] - village2[0]) + abs(village1[1] - village2[1])


def distance(position1, position2):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])



def print_optimal_tour(optimal_tour, graph):
    villages = graph["villages"]
    drones = graph["drones"]
    currently_drone = 0
    for i in optimal_tour:
        data_1 = i[0]
        data_2 = i[1]
        if (data_1 in drones.values() and data_2 in villages.values()):
            key_drones = get_key_from_value(drones, data_1)
            key_villages = get_key_from_value(villages, data_2)
            if (key_drones != currently_drone):
                currently_drone = key_drones
            print (f'Le drone {currently_drone} va au village {key_villages}')
            continue
        if (data_1 in villages.values() and data_2 in villages.values()):
            key_villages1 = get_key_from_value(villages,data_1)
            key_villages2 = get_key_from_value(villages, data_2)
            print(f'Le drone {currently_drone} va du village {key_villages1} au village {key_villages2}')
            continue




def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Si la valeur n'est pas trouvée
        

N = 100
my_graph = read_graph(N,"village3.txt")
tour_optimal = a_star_search(my_graph,heuristic)

print(my_graph)
print(tour_optimal)
print_optimal_tour(tour_optimal, my_graph)