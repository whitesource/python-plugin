class ResourceInfo:
    def __init__(self, display_name=None, link=None, licenses=None):
        if licenses is None:
            self.licenses = []
        else:
            self.licenses = licenses
        self.link = link
        self.displayName = display_name


def from_dict(info_dict):
    """ Creates a ResourceInfo object from a dict """

    resource_info = ResourceInfo()

    if 'licenses' in info_dict:
        resource_info.licenses = info_dict['licenses']

    if 'link' in info_dict:
        resource_info.link = info_dict['link']

    if 'displayName' in info_dict:
        resource_info.displayName = info_dict['displayName']

    return resource_info
