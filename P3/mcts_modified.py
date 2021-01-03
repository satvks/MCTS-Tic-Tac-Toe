
from mcts_node import MCTSNode
from random import choice
import math

num_nodes = 700
explore_faction = 2.


def traverse_nodes(node, board, state, identity):   # selection
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
                    the currnode.
        board:      The game setup.
                    the board ig...
        state:      The state of the game.
                    where we @ in tha game. should have access to available moves?
        identity:   The bot's identity, either 'red' or 'blue'. who movin.

    Returns:        A node from which the next stage of the search can proceed.

    """
    # check if currnode has children: true-> calculate ucbs and select max. traverse those nodes.
    # this selection does a lot more than select. Some of this should be implemented in think. i think ahaha.

    while len(node.child_nodes) > 0:
        node = max_ucb(node)
        state = board.next_state(state, node.parent_action)
    return node, state

    # Hint: return leaf_node


def expand_leaf(node, board, state):                # expansion
    """ Adds new leaves to the tree by creating a new child node for the given node.
    Every possible move is being "simulated" here. Each possible move is created as
    a new state in the tree
    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    All added child nodes.

    """
    nodes = []

    while len(node.untried_actions) != 0:
        action = choice(node.untried_actions)
        node.untried_actions.remove(action)

        new_state = board.next_state(state, action)
        new_node = MCTSNode(node, action, board.legal_actions(new_state))

        node.child_nodes[action] = new_node
        nodes.append(new_node)

    return nodes
    # Hint: return new_node


def rollout(board, state):                          # simulation - u kno wut-eet-eeez
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The value of a win, loss, or draw.

    """
    while not board.is_ended(state):
        # action = winning_action(board, state)
        state = board.next_state(state, choice(board.legal_actions(state)))
    return board.win_values(state)      # ^ choice(board.legal_actions(state))


def backpropagate(node, won):                       # yeugckh/yeuckgh
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game. Will b an int.

    """
    while node is not None:
        node.wins += won
        node.visits += 1
        node = node.parent
    return


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    step = 0
    global explore_faction

    while step < num_nodes:
        # Do MCTS - This is all you!
        leaf_node, sampled_game = traverse_nodes(root_node, board, state, identity_of_bot)
        new_nodes = expand_leaf(leaf_node, board, sampled_game)
        if len(new_nodes) == 0:
            break
        step += len(new_nodes)
        done_rollouts = {}
        for roll_node in new_nodes:
            if tuple(sorted(roll_node.untried_actions)) in done_rollouts.keys():
                backpropagate(roll_node, done_rollouts[tuple(sorted(roll_node.untried_actions))])
            else:
                won = rollout(board, board.next_state(sampled_game, roll_node.parent_action))[identity_of_bot]
                backpropagate(roll_node, won)
                if won == 1:
                    explore_faction += .25          # if a game is won, seek out games along this path.
                elif won == 0 and explore_faction > 0.25:
                    explore_faction -= 0.25         # if a game is lost, seek fewer games from this path.
                done_rollouts[tuple(sorted(roll_node.untried_actions))] = won

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    maximum = -1
    max_node = root_node
    for child in root_node.child_nodes.values():
        # print("Score: ", child.wins / child.visits)
        if child is not None and (child.wins/child.visits) > maximum:
            max_node = child
            maximum = (child.wins/child.visits)

    # print("Max Node: ", max_node, " - ", max_node.wins/max_node.visits)
    return max_node.parent_action


def max_ucb(node):
    maximum = -1
    max_node = node
    parent_visits = node.visits
    # check if ucb = infinity/undefined/None. Doesn't this mean, no children?
    for child in node.child_nodes.values():
        wv_ratio = child.wins / child.visits
        other_part = explore_faction * (math.sqrt(math.log(parent_visits) / child.visits))
        ucb = wv_ratio + other_part
        if child is not None and ucb > maximum:
            max_node = child
            maximum = ucb

    return max_node

def winning_action(board, state):                   # Returns: an action that would win a board.
    legal_actions = board.legal_actions(state)      # a list of legal moves
    while legal_actions != []:                      # get legal_move in current state
        action = choice(legal_actions)              # select a random action
        legal_actions.remove(action)
        next_state = board.next_state(state, action)  # get next_state
        for move in legal_actions:
            if board.is_legal(next_state, move):   # somehow check if prev grid is still legal
                return move
    return choice(board.legal_actions(state))       # placeholder return choice

