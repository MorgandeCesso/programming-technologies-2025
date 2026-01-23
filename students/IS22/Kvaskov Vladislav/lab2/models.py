from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True, generated=True )
    username_db = fields.CharField(max_length=255)
    user_id_db = fields.BigIntField(unique=True)

    class Meta:
        table = "user"

class MessageDB(Model):
    id = fields.IntField(pk=True, generated=True)
    message_db = fields.TextField()
    response_db = fields.TextField()
    user_id = fields.ForeignKeyField('models.User', related_name='messages', to_field='user_id_db')
    created_db = fields.DatetimeField(auto_now_add=True)
    context_db = fields.BooleanField(default=True)
   
    class Meta:
        table = "message"