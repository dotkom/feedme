from django.contrib.auth import get_user_model

User = get_user_model()

# Christian fant dette
# With the default User model these will be 'auth.User' and 'auth.user'
# so instead of using orm['auth.User'] we can use orm[user_orm_label]
user_name = User.__name__
user_table = User._meta.db_table
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)
