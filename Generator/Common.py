def lower_nullable(text):
    """
    None-safe version of 'str.lower'
    @param text: the text to convert to lower-case
    """
    if text is None:
        return None

    return text.lower()
    
def compare_nullable_icase(lhs, rhs):
    """
    None-safe case-insensitive comparison
    @param lhs: an item to be compared to rhs
    @param rhs: an item to be compared to lhs
    """
    if lhs is None and rhs is None:
        return True
    elif lhs is None or rhs is None:
        return False

    return lhs.lower() == rhs.lower()