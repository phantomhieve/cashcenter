from whitenoise.storage import CompressedManifestStaticFilesStorage

class StrictFalseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manifest_strict = False
        self.strict = False
