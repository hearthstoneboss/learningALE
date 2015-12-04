from learningALE.learners.learner import learner
from learningALE.handlers.actionhandler import ActionHandler, ActionPolicy
from learningALE.handlers.experiencehandler import ExperienceHandler
from learningALE.handlers.trainhandler import TrainHandler
from learningALE.learners.nns import CNN


class DoubleDQNLearner(learner):
    def __init__(self, skip_frame, num_actions, load=None):
        super().__init__()

        rand_vals = (1, 0.1, 1000000/skip_frame)  # starting at 1 anneal eGreedy policy to 0.1 over 1,000,000*skip_frame
        self.action_handler = ActionHandler(ActionPolicy.eGreedy, rand_vals)

        self.exp_handler = ExperienceHandler(1000000/skip_frame)
        self.train_handler = TrainHandler(32, 0.9, num_actions)
        self.cnn = CNN((None, skip_frame, 86, 80), num_actions, .1)
        self.target_cnn = self.cnn.copy()

        if load is not None:
            self.cnn.load(load)

    def copy_new_target(self):
        self.target_cnn = self.cnn.copy()

    def get_action(self, game_input):
        return self.cnn.get_output(game_input)[0]

    def get_game_action(self, game_input):
        return self.action_handler.action_vect_to_game_action(self.get_action(game_input))

    def frames_processed(self, frames, action_performed, reward):
        self.exp_handler.add_experience(frames, self.action_handler.game_action_to_action_ind(action_performed), reward)
        self.train_handler.train_double(self.exp_handler, self.cnn, self.target_cnn)
        self.action_handler.anneal()

    def set_legal_actions(self, legal_actions):
        self.action_handler.set_legal_actions(legal_actions)

    def save(self, file):
        self.cnn.save(file)

    def get_cost_list(self):
        return self.train_handler.costList