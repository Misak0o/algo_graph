import heapq

def read_graph(N, nom_fichier):
    graphe = {'villages': {}, 'obstacles': [], 'deplacements': [], 'drone': None}
    ordered_villages = []

    with open(nom_fichier, 'r') as f:
        for ligne in f:
            ligne = ligne.strip()
            entite, coordonnees = ligne.split(' : ')

            if entite == 'D':
                graphe['drone'] = tuple(map(int, coordonnees.strip()[1:-1].split(',')))
            elif entite.isdigit():
                identite = int(entite)
                x, y = map(int, coordonnees.strip()[1:-1].split(','))
                if 1 <= x <= N and 1 <= y <= N:  # Vérification des coordonnées valides
                    graphe['villages'][identite] = (x, y)
                    ordered_villages.append((x, y))
                else:
                    print(f"Attention: Les coordonnées du village {identite} ne sont pas valides.")

    graphe['ordered_villages'] = ordered_villages
    return graphe


def a_star_search(graph, heuristic):
    # Initialiser l'état initial à partir des données du graphe
    initial_state = {
        'drone_positions': [graph['drone']],
        'remaining_villages': list(graph['villages'].values()),
        'path': [],
        'g_score': 0,
        'h_score': heuristic(graph['drone'], list(graph['villages'].values())[-1]),
        'f_score': heuristic(graph['drone'], list(graph['villages'].values())[-1]),
        'hash': (graph['drone'],) + tuple(graph['villages'].values())
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
    # Heuristique : distance de Manhattan entre les deux villages
    return abs(village1[0] - village2[0]) + abs(village1[1] - village2[1])

def distance(position1, position2):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

N = 100
my_graph = read_graph(N,"village1.txt")
tour_optimal = a_star_search(my_graph,heuristic)

print(my_graph)
print(f'tour_optimal : {tour_optimal}')