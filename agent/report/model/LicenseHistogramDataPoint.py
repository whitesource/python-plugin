class LicenseHistogramDataPoint:
    def __init__(self, name, occurrences, height):
        self.height = height
        self.occurrences = occurrences
        self.name = name
        self.license_name_max_length = 16;

    def get_short_name(self):
        short_name = self.name
        if len(self.name) > self.license_name_max_length:
            short_name[0:self.license_name_max_length-2] + ".."

        return short_name