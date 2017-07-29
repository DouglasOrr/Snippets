
class Config:
    def __init__(self, description="Unknown optimization problem"):
        """Create a configuration instance.
        This makes it easy to define and run TreeLearn searches.
        For every search, a single initialization, stepping and evaluation procedure should be
        specified using ``init``, ``step`` and ``eval``."""
        self._description = description
        self._repositories = {}

    def repository(self, name, path):
        """Add a respository to monitor; note that ${name} will be substituted into
         every command that runs, so make sure it is unique."""
        if name in self._repositories:
            raise ArgumentError("Repository '%s' already exists (as '%s')" % (name, self._repositories[name]))
        self._repositories[name] = path

    def init(self, command, options={}):
        """Set the model initializer. Models will be initialized by running ``command``.
        The command may depend on ${REPO_NAME} for every repository name provided to ``repository``
        (a local path to the repository will be substituted).
        The command should write the created model to ${TARGET}.
        Finally, the command may depend on ${OPTIONS}, which is a quoted, JSON-encoded configuration,
        generated according to the search, constrained by the ``options`` argument."""
        self._init = None # TODO

    def step(self, command, options={})
        """Set the model stepper. Models will be advanced by running ``command``.
        The command may depend on ${REPO_NAME} for every repository name provided to ``repository``
        (a local path to the repository will be substituted).
        The command should read the original model from ${SOURCE}, and write the final model to ${TARGET}.
        Finally, the command may depend on ${OPTIONS}, which is a quoted, JSON-encoded configuration,
        generated according to the search, constrained by the ``options`` argument."""
        self._step = None # TODO

    def eval(self, command)
        """Set the model evaluator. Models will be evaluated by running ``command``.
        The command may depend on ${REPO_NAME} for every repository name provided to ``repository``
        (a local path to the repository will be substituted).
        The command should read the model to evaluate from ${SOURCE}.
        This command may not take any options."""
        self._eval = None # TODO

    def run(self):
        print("TODO: running")
