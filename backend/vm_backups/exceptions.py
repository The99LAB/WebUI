class jobManagerException(Exception):
    def __init__(self, errormsg):
        self.message = errormsg
        super().__init__(self.message)

class restoreException(Exception):
    def __init__(self, errormsg):
        self.message = errormsg
        super().__init__(self.message)

class backupException(Exception):
    def __init__(self, errormsg):
        self.message = errormsg
        super().__init__(self.message)