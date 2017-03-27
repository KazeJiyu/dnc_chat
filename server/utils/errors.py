import sys

def print_err(*args, **kwargs):
    """
    Same as print() yet writes in stderr
    """
    print(*args, file=sys.stderr, **kwargs)
    
def abort_if(predicate, message=""):
    """
    Raises a `:class:ValueError` if the given predicate is `True`.
    
    This method may be used in order to improve the readability when
    multiple predicates have to be checked.
    
    Parameters:
    -----------
        predicate (function[bool]): the predicate to check
        message (str): the error message
    """
    if predicate():
        raise ValueError(message)