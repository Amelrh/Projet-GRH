
def is_responsable_rh(user):
    return user.is_superuser or user.groups.filter(name='Responsables RH').exists()

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

def is_utilisateur(user):
    return user.groups.filter(name='Utilisateurs').exists()

