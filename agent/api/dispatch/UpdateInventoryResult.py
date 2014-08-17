class UpdateInventoryResult:

    def __init__(self, organization, updated_projects, created_projects):
        self.organization = organization
        self.created_projects = created_projects
        self.updated_projects = updated_projects

