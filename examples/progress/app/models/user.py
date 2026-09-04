"""User — has many posts, belongs to many roles, morphs comments."""

from __future__ import annotations

from avalon.auth import AuthenticatableMixin
from avalon.orm import Model, relation


class User(AuthenticatableMixin, Model):
    fillable = ("email", "name", "password", "remember_token", "api_token")
    hidden = ("password", "remember_token")

    @relation
    def posts(self):
        from app.models.post import Post

        return self.has_many(Post)

    @relation
    def roles(self):
        from app.models.role import Role

        return self.belongs_to_many(Role).with_pivot("level")

    @relation
    def comments(self):
        from app.models.comment import Comment

        return self.morph_many(Comment, "commentable")
