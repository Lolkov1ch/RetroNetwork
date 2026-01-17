def user_directory_path(instance, filename):
    user_id = instance.user.id

    # if hasattr(instance, 'post') and instance.post_id:
    #     return f'{user_id}/posts/{instance.post_id}/{filename}'
    # elif hasattr(instance, 'message') and instance.message_id:
    #     return f'{user_id}/messenger/{instance.message_id}/{filename}'

    return f'{user_id}/{filename}'

# tag will be used