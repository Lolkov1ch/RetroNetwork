def user_directory_path(instance, filename):
    user_id = instance.user.id
    return f'{user_id}/{filename}'
