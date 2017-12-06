class Action:
    """
    Action class
    """

    def __init__(self, resource_type, run_type):
        """
        Constructor
        :param resource_type: resource type of load test
        :param run_type: type of run
        """
        self._resource_type = resource_type
        self._run_type = run_type

    def __repr__(self):
        """Convert Action object to string"""
        return '<Action(resource_type={resource}, run_type={run}>'.format(resource=self._resource_type,
                                                                          run=self._run_type)


class User:
    """
    User class
    """

    def __init__(self, id, type, name, action):
        """
        Constructor
        :param id: user id
        :param type: user type
        :param name: user name
        :param action: user action
        """
        self._id = id
        self._type = type
        self._name = name
        self._action = action

    def __repr__(self):


class:

    def __init__(self, id, type, user, lt_path, run_type, ):
        self.id = id
        self._user_type = type
        self._user = user
        self._lt_path = lt_path
        self._run_type = run_type
