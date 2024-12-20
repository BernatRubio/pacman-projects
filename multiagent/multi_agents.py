# multi_agents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattan_distance
from game import Directions, Actions
from pacman import GhostRules
import random, util
from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def get_action(self, game_state):
        """
        You do not need to change this method, but you're welcome to.

        get_action chooses among the best options according to the evaluation function.

        Just like in the previous project, get_action takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legal_moves = game_state.get_legal_actions()

        # Choose one of the best actions
        scores = [self.evaluation_function(game_state, action) for action in legal_moves]
        best_score = max(scores)
        best_indices = [index for index in range(len(scores)) if scores[index] == best_score]
        chosen_index = random.choice(best_indices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legal_moves[chosen_index]

    def evaluation_function(self, current_game_state, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (new_food) and Pacman position after moving (new_pos).
        new_scared_times holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successor_game_state = current_game_state.generate_pacman_successor(action)
        new_pos = successor_game_state.get_pacman_position()
        new_food = successor_game_state.get_food().as_list()
        new_ghost_states = successor_game_state.get_ghost_states()
        new_scared_times = [ghostState.scared_timer for ghostState in new_ghost_states]
        
        "*** YOUR CODE HERE ***"
        # Initialize evaluation score
        score = successor_game_state.get_score()  # Start with the game's current score

        # Feature 1: Distance to the closest food
        if new_food:
            food_distances = [manhattan_distance(new_pos, food) for food in new_food]
            closest_food_distance = min(food_distances)
            score += 10 / closest_food_distance  # Closer food gives higher score

        # Feature 2: Ghost distances and scared times
        for ghost_state, scared_time in zip(new_ghost_states, new_scared_times):
            ghost_pos = ghost_state.get_position()
            ghost_distance = manhattan_distance(new_pos, ghost_pos)

            if scared_time > 0:  # Ghost is scared
                # Closer distance to scared ghost is good, incentivize approaching
                score += 200 / ghost_distance if ghost_distance > 0 else 200
            else:  # Ghost is not scared
                # Penalize being too close to an active ghost
                if ghost_distance > 0:
                    score -= 100 / ghost_distance

        # Feature 3: Number of remaining food pellets
        score -= 10 * len(new_food)  # Fewer food pellets left is better

        return score

def score_evaluation_function(current_game_state):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return current_game_state.get_score()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, eval_fn='score_evaluation_function', depth='2'):
        super().__init__()
        self.index = 0 # Pacman is always agent index 0
        self.evaluation_function = util.lookup(eval_fn, globals())
        self.depth = int(depth) 

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def get_action(self, game_state):
        """
        Returns the minimax action from the current game_state using self.depth
        and self.evaluation_function.

        Here are some method calls that might be useful when implementing minimax.
        game_state.get_legal_actions(agent_index):
        Returns a list of legal actions for an agent
        agent_index=0 means Pacman, ghosts are >= 1

        game_state.generate_successor(agent_index, action):
        Returns the successor game state after an agent takes an action

        game_state.get_num_agents():
        Returns the total number of agents in the game

        game_state.is_win():
        Returns whether or not the game state is a winning state

        game_state.is_lose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        import sys

        num_agents = game_state.get_num_agents()
        pacman_index = 0
        INITIAL_DEPTH = 0

        def max_func(game_state, depth):
            # Base case for Pacman
            if depth == self.depth or game_state.is_win() or game_state.is_lose():
                return self.evaluation_function(game_state), None

            max_score = -sys.maxsize
            best_action = None
            
            # Loop through all possible actions for Pacman
            for action in game_state.get_legal_actions(pacman_index):
                successor_state = game_state.generate_successor(pacman_index, action)
                score, _ = min_func(1, depth, successor_state)  # Min function for first ghost
                
                if score > max_score:
                    max_score = score
                    best_action = action

            return max_score, best_action

        def min_func(agent_index, depth, game_state):
            # Base case for Ghosts
            if game_state.is_win() or game_state.is_lose():
                return self.evaluation_function(game_state), None

            min_score = sys.maxsize
            best_action = None
            
            # Loop through all possible actions for this ghost
            for action in game_state.get_legal_actions(agent_index):
                successor_state = game_state.generate_successor(agent_index, action)
                
                if agent_index == num_agents - 1:  # Last ghost moves, Pacman goes next
                    score, _ = max_func(successor_state, depth + 1)
                else:  # Next ghost moves
                    score, _ = min_func(agent_index + 1, depth, successor_state)

                if score < min_score:
                    min_score = score
                    best_action = action

            return min_score, best_action

        _, action = max_func(game_state, INITIAL_DEPTH)
        return action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def get_action(self, game_state):
        """
        Returns the minimax action using self.depth and self.evaluation_function
        """
        "*** YOUR CODE HERE ***"
        import sys

        num_agents = game_state.get_num_agents()
        pacman_index = 0
        INITIAL_DEPTH = 0

        def max_func(game_state, depth, alpha, beta):
            if depth == self.depth or game_state.is_win() or game_state.is_lose():
                return self.evaluation_function(game_state), None

            max_score = -sys.maxsize
            best_action = None
            
            for action in game_state.get_legal_actions(pacman_index):
                successor_state = game_state.generate_successor(pacman_index, action)
                score, _ = min_func(1, depth, successor_state, alpha, beta)
                
                if score > max_score:
                    max_score = score
                    best_action = action
                
                if max_score > beta: # Beta-cut (we don't take into account equality to avoid expanding unnecessary nodes)
                    return max_score, best_action
                
                alpha = max(alpha , max_score) # Alpha is updated with the max value (MAX is playing)

            return max_score, best_action

        def min_func(agent_index, depth, game_state, alpha, beta):
            if game_state.is_win() or game_state.is_lose():
                return self.evaluation_function(game_state), None

            min_score = sys.maxsize
            best_action = None
            
            for action in game_state.get_legal_actions(agent_index):
                successor_state = game_state.generate_successor(agent_index, action)
                
                if agent_index == num_agents - 1:
                    score, _ = max_func(successor_state, depth + 1, alpha, beta)
                else:
                    score, _ = min_func(agent_index + 1, depth, successor_state, alpha, beta)

                if score < min_score:
                    min_score = score
                    best_action = action

                if min_score < alpha: # Alpha-cut (we don't take into account equality to avoid expanding unnecessary nodes)
                    return min_score, best_action
                
                beta = min(min_score, beta) #  Beta is updated with the min value (MIN is playing)
                
            return min_score, best_action

        alpha = -sys.maxsize
        beta = sys.maxsize
        _, action = max_func(game_state, INITIAL_DEPTH, alpha, beta)
        return action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def get_action(self, game_state):
        """
        Returns the expectimax action using self.depth and self.evaluation_function

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raise_not_defined()

def better_evaluation_function(current_game_state):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raise_not_defined()
    


# Abbreviation
better = better_evaluation_function
