from dis_command.discommand.exceptions import ConverterError

class CantReachAPI(Exception):
    pass

class ArgConvertError(ConverterError):
    pass

class CommandCheckError(Exception):
    pass

class PremiumCheckError(Exception):
    pass