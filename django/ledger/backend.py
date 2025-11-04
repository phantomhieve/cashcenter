from user.models import UserGroup


def getUserGroup(user):
    """
    Get the user group for a given user.
    
    Returns the UserGroup instance if the user is a primary_user or main_user,
    otherwise returns None.
    """
    try:
        return user.main_user
    except UserGroup.DoesNotExist:
        try:
            return user.primary_user
        except UserGroup.DoesNotExist:
            return None


def getUsersFromGroup(user):
    """
    Get all users in the same group as the given user.
    
    Returns a list containing the primary_user and main_user if they exist,
    otherwise returns a list with just the user.
    """
    user_group = getUserGroup(user)
    if user_group:
        return [
            user_group.primary_user,
            user_group.main_user
        ]
    return [user]
