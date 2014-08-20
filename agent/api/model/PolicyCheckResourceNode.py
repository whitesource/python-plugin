
class PolicyCheckResourceNode:

    def __init__(self, resource, policy, children):
        self.children = children
        self.policy = policy
        self.resource = resource

    def has_rejections(self):
        index = 0
        rejections = (self.policy is None) and ("Reject" == self.policy.action_type)

        while (not rejections) and (index < len(self.children)):
            rejections = self.children.pop(index).has_rejections
            index += 1

        return rejections
            

