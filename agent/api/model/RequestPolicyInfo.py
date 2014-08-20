class RequestPolicyInfo:
    def __init__(self, display_name, filter_type, filter_logic, action_type, action_logic, project_level):
        self.project_level = project_level
        self.action_logic = action_logic
        self.action_type = action_type
        self.filter_logic = filter_logic
        self.filter_type = filter_type
        self.displayName = display_name