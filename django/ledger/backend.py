from user.models import UserGroup

def getUserGroup(user):
    try:
        user_group = user.main_user
    except:
        try:
            user_group = user.primary_user
        except:
            user_group = None
    return user_group

def getUsersFromGroup(user):
    user_group = getUserGroup(user)
    if user_group:
        return [
            user_group.primary_user, 
            user_group.main_user
        ]
    return [user]
