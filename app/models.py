from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    ORM Model for User corresponding to the user DB table
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    age = fields.IntField(null=True)

    def __str__(self):
        return f"{self.id}, {self.name}, {self.age}"

    class Meta:
        table = "users"
