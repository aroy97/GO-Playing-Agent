import copy
import random

go_mini_board_size = 5
input_file_from_game = 'input.txt'
output_file_to_game = 'output.txt'
test_input_file_name = "input.txt"


def reading_input_file_for_game(input_file_name):
    input_file_data = list()
    with open(input_file_name, 'r') as game_input_file:
        for data_line in game_input_file.readlines():
            input_file_data.append(data_line.strip())
    last_game_board_state_read = list()
    current_game_board_state_read = list()
    for data_line in range(1, go_mini_board_size + 1):
        data_in_current_line = [int(location_data) for location_data in input_file_data[data_line]]
        last_game_board_state_read.append(data_in_current_line)
    for data_line in range(go_mini_board_size + 1, 2 * go_mini_board_size + 1):
        data_in_current_line = [int(location_data) for location_data in input_file_data[data_line]]
        current_game_board_state_read.append(data_in_current_line)
    return int(input_file_data[0]), last_game_board_state_read, current_game_board_state_read


def writing_output_file_for_game(output_file_name, movement_in_current_move_to_play):
    with open(output_file_name, 'w') as file_to_write:
        if movement_in_current_move_to_play == 'PASS':
            file_to_write.write(movement_in_current_move_to_play)
        else:
            file_to_write.write(
                str(movement_in_current_move_to_play[0]) + ',' + str(movement_in_current_move_to_play[1]))


def alpha_beta_pruned_minimax(current_game_board_state_minimax, last_game_board_state_minimax,
                              maximum_depth_of_algorithm, alpha_for_pruning, beta_for_pruning, side_of_player_minimax):
    possible_list_of_moves = list()
    best_move_score = 0
    current_game_board_state_minimax_copy = copy.deepcopy(current_game_board_state_minimax)
    for possible_move in find_valid_moves_for_minimax(current_game_board_state_minimax, last_game_board_state_minimax,
                                                      side_of_player_minimax):
        game_board_next_state = copy.deepcopy(current_game_board_state_minimax)
        game_board_next_state[possible_move[0]][possible_move[1]] = side_of_player_minimax
        game_board_next_state = remove_conquered_stones(game_board_next_state, 3 - side_of_player_minimax)
        heuristic_value = calculate_heuristic_of_a_path(game_board_next_state, 3 - side_of_player_minimax)
        evaluation = helper_function_for_minimax(game_board_next_state, current_game_board_state_minimax_copy,
                                                 maximum_depth_of_algorithm,
                                                 alpha_for_pruning, beta_for_pruning, heuristic_value,
                                                 3 - side_of_player_minimax)
        current_path_score_in_minimax = evaluation * -1
        if current_path_score_in_minimax > best_move_score or not possible_list_of_moves:
            best_move_score = current_path_score_in_minimax
            possible_list_of_moves = [possible_move]
            alpha_for_pruning = best_move_score
        elif current_path_score_in_minimax == best_move_score:
            possible_list_of_moves.append(possible_move)

    return possible_list_of_moves


def find_valid_moves_for_minimax(current_game_board_state_validator, last_game_board_state_validator,
                                 side_of_player_validator):
    list_of_valid_moves = list()
    for game_board_row_validator in range(go_mini_board_size):
        for game_board_column_validator in range(go_mini_board_size):
            if possible_move_after_stone_removals(current_game_board_state_validator, last_game_board_state_validator,
                                                  side_of_player_validator, game_board_row_validator,
                                                  game_board_column_validator):
                list_of_valid_moves.append((game_board_row_validator, game_board_column_validator))
    return list_of_valid_moves


def possible_move_after_stone_removals(current_game_board_state_possible, last_game_board_state_possible,
                                       side_of_player_possible, game_board_row_possible, game_board_column_possible):
    if current_game_board_state_possible[game_board_row_possible][game_board_column_possible] != 0:
        return False
    current_game_board_copy = copy.deepcopy(current_game_board_state_possible)
    current_game_board_copy[game_board_row_possible][game_board_column_possible] = side_of_player_possible
    dead_pieces = spot_stones_which_can_be_conquered(current_game_board_copy, 3 - side_of_player_possible)
    current_game_board_copy = remove_conquered_stones(current_game_board_copy, 3 - side_of_player_possible)
    if find_whether_cluster_has_liberty(current_game_board_copy, game_board_row_possible,
                                        game_board_column_possible) >= 1 and (
            not dead_pieces or not check_ko_rules(last_game_board_state_possible, current_game_board_copy)):
        return True


def spot_stones_which_can_be_conquered(current_game_board_spot_stones, side_of_player_spot_stone):
    can_be_conquered_stones = []
    for game_board_row_spot in range(go_mini_board_size):
        for game_board_column_spot in range(go_mini_board_size):
            if current_game_board_spot_stones[game_board_row_spot][game_board_column_spot] == side_of_player_spot_stone:
                if not find_whether_cluster_has_liberty(current_game_board_spot_stones, game_board_row_spot,
                                                        game_board_column_spot) and \
                        (game_board_row_spot, game_board_column_spot) not in can_be_conquered_stones:
                    can_be_conquered_stones.append((game_board_row_spot, game_board_column_spot))
    return can_be_conquered_stones


def remove_conquered_stones(current_game_board_conquered_stone, side_of_player_conquered_stone):
    dead_stones = spot_stones_which_can_be_conquered(current_game_board_conquered_stone, side_of_player_conquered_stone)
    if not dead_stones:
        return current_game_board_conquered_stone
    new_board = conquer_stones(current_game_board_conquered_stone, dead_stones)
    return new_board


def conquer_stones(current_game_board_conquer, conquer_stone_location):
    for stone in conquer_stone_location:
        current_game_board_conquer[stone[0]][stone[1]] = 0
    return current_game_board_conquer


def find_whether_cluster_has_liberty(current_game_board_liberty, game_board_row_liberty, game_board_column_liberty):
    count = 0
    for point in find_cluster_of_same_team(current_game_board_liberty, game_board_row_liberty,
                                           game_board_column_liberty):
        for neighbor in find_neighbor_stones(current_game_board_liberty, point[0], point[1]):
            if current_game_board_liberty[neighbor[0]][neighbor[1]] == 0:
                count += 1
    return count


def find_cluster_of_same_team(current_game_board_ally, game_board_row_ally, game_board_column_ally):
    queue_of_stones = [(game_board_row_ally, game_board_column_ally)]
    cluster_of_stones = list()
    while queue_of_stones:
        current_stone = queue_of_stones.pop(0)
        cluster_of_stones.append(current_stone)
        for neighbor in find_ally_neighbors(current_game_board_ally, current_stone[0], current_stone[1]):
            if neighbor not in queue_of_stones and neighbor not in cluster_of_stones:
                queue_of_stones.append(neighbor)
    return cluster_of_stones


def find_neighbor_stones(current_game_board_neighbor_find, game_board_row_neighbor_find,
                         game_board_column_neighbor_find):
    board = remove_conquered_stones(current_game_board_neighbor_find,
                                    (game_board_row_neighbor_find, game_board_column_neighbor_find))
    neighboring = [(game_board_row_neighbor_find - 1, game_board_column_neighbor_find),
                   (game_board_row_neighbor_find + 1, game_board_column_neighbor_find),
                   (game_board_row_neighbor_find, game_board_column_neighbor_find - 1),
                   (game_board_row_neighbor_find, game_board_column_neighbor_find + 1)]
    return [point for point in neighboring if 0 <= point[0] < go_mini_board_size and 0 <= point[1] < go_mini_board_size]


def find_ally_neighbors(current_game_board_neighbor, game_board_row_neighbor, game_board_column_neighbor):
    same_team_stones = list()
    for point in find_neighbor_stones(current_game_board_neighbor, game_board_row_neighbor, game_board_column_neighbor):
        if current_game_board_neighbor[point[0]][point[1]] == current_game_board_neighbor[game_board_row_neighbor][
            game_board_column_neighbor]:
            same_team_stones.append(point)
    return same_team_stones


def check_ko_rules(last_game_board_state_ko, current_game_board_ko):
    for game_board_row_ko in range(go_mini_board_size):
        for game_board_column_ko in range(go_mini_board_size):
            if current_game_board_ko[game_board_row_ko][game_board_column_ko] != \
                    last_game_board_state_ko[game_board_row_ko][game_board_column_ko]:
                return False
    return True


def calculate_heuristic_of_a_path(next_game_state_heuristic, player_heuristic_modified):
    opponent_score, player_score, player_path_heuristic, opponent_path_heuristic = 0, 0, 0, 0
    for game_board_row_heuristic in range(go_mini_board_size):
        for game_board_column_heuristic in range(go_mini_board_size):
            if next_game_state_heuristic[game_board_row_heuristic][game_board_column_heuristic] == side_of_player:
                player_score += 1
                player_path_heuristic += (
                        player_score + find_whether_cluster_has_liberty(next_game_state_heuristic,
                                                                        game_board_row_heuristic,
                                                                        game_board_column_heuristic))
            elif next_game_state_heuristic[game_board_row_heuristic][game_board_column_heuristic] == 3 - side_of_player:
                opponent_score += 1
                opponent_path_heuristic += (
                        opponent_score + find_whether_cluster_has_liberty(next_game_state_heuristic,
                                                                          game_board_row_heuristic,
                                                                          game_board_column_heuristic))

    if player_heuristic_modified == side_of_player:
        return player_path_heuristic - opponent_path_heuristic
    return opponent_path_heuristic - player_path_heuristic


def helper_function_for_minimax(current_game_state, previous_game_state, depth_of_pruning, alpha, beta, heuristic_value,
                                player_to_play_next):
    if depth_of_pruning == 0:
        return heuristic_value
    best_value_achieved = heuristic_value
    curr_state_copy = copy.deepcopy(current_game_state)
    for valid_move in find_valid_moves_for_minimax(current_game_state, previous_game_state, player_to_play_next):
        next_game_state = copy.deepcopy(current_game_state)
        next_game_state[valid_move[0]][valid_move[1]] = player_to_play_next
        next_game_state = remove_conquered_stones(next_game_state, 3 - player_to_play_next)
        future_heuristic = calculate_heuristic_of_a_path(next_game_state, 3 - player_to_play_next)
        value_of_best_move_in_path = helper_function_for_minimax(next_game_state, curr_state_copy, depth_of_pruning - 1,
                                                                 alpha, beta, future_heuristic, 3 - player_to_play_next)
        score_of_current_path = -1 * value_of_best_move_in_path
        if score_of_current_path > best_value_achieved:
            best_value_achieved = score_of_current_path
        new_score_of_current_path = -1 * best_value_achieved
        if player_to_play_next == 3 - side_of_player:
            heuristic_of_player_path = new_score_of_current_path
            if heuristic_of_player_path < alpha:
                return best_value_achieved
            if best_value_achieved > beta:
                beta = best_value_achieved
        elif player_to_play_next == side_of_player:
            heuristic_of_opponent_path = new_score_of_current_path
            if heuristic_of_opponent_path < beta:
                return best_value_achieved
            if best_value_achieved > alpha:
                alpha = best_value_achieved
    return best_value_achieved


side_of_player, last_game_board_state, current_game_board_state = reading_input_file_for_game(input_file_from_game)

number_of_stones = 0
center_move_check = False
for game_board_row in range(5):
    for game_board_column in range(5):
        if current_game_board_state[game_board_row][game_board_column] != 0:
            if game_board_row == 2 and game_board_column == 2:
                center_move_check = True
            number_of_stones += 1
if (number_of_stones == 0 and side_of_player == 1) or (
        number_of_stones == 1 and side_of_player == 2 and center_move_check is False):
    move_to_play = [(2, 2)]
else:
    move_to_play = alpha_beta_pruned_minimax(current_game_board_state, last_game_board_state, 3, -1000, -1000,
                                             side_of_player)
if not move_to_play:
    random_move_to_play = ['PASS']
else:
    random_move_to_play = random.choice(move_to_play)

writing_output_file_for_game(output_file_to_game, random_move_to_play)