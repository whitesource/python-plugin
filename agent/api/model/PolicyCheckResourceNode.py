from agent.api.model import ResourceInfo
from agent.api.model import RequestPolicyInfo


class PolicyCheckResourceNode:
    def __init__(self, resource=None, policy=None, children=None):
        self.resource = resource
        self.policy = policy
        if children is None:
            self.children = []
        else:
            self.children = children

    def has_rejections(self):
        """ Checks if any of the children of the node have rejection policy """

        index = 0

        if self.policy is None:
            rejections = not self.policy is None
        else:
            rejections = "Reject" == self.policy.actionType

        while (not rejections) and (index < len(self.children)):
            child = self.children[index]
            rejections = child.has_rejections()
            index += 1

        return rejections


def from_dict(node_dict):
    """ Creates a ResourceNode object from dict """

    policy_check_node = PolicyCheckResourceNode()

    if 'resource' in node_dict.keys():
        if node_dict['resource']:
            policy_check_node.resource = ResourceInfo.from_dict(node_dict['resource'])

    if 'policy' in node_dict.keys():
        if node_dict['policy']:
            policy_check_node.policy = RequestPolicyInfo.from_dict(node_dict['policy'])

    if 'children' in node_dict.keys():
        if node_dict['children']:
            # populate children
            children_dict = node_dict['children']
            for child in children_dict:
                child_node = from_dict(child)
                policy_check_node.children.append(child_node)

    return policy_check_node


def find_rejected_node(node):
    """ Recursively find the libraries that have a rejected policy """

    rejected_nodes = []

    if node.policy:
        if node.policy.actionType == "Reject":
            rejected_nodes.append(node)
    if node.children:
        for child in node.children:
            rejected_nodes += find_rejected_node(child)

    return rejected_nodes
