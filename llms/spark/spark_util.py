class SparkUtil:

    @classmethod
    def get_domain(cls, version):
        domain = None
        if version == 'v1.1':
            domain = "general"
        elif version == 'v2.1':
            domain = "generalv2"
        elif version == 'v3.1':
            domain = "generalv3"

        return domain
