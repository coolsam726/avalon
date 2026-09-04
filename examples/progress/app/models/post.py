"""Post — belongs to a user; soft deletes + published scope."""

from __future__ import annotations

from avalon.orm import Model, SoftDeletes, relation


class Post(SoftDeletes, Model):
    fillable = ("title", "user_id", "published", "views")
    casts = {"published": "bool", "views": "int"}  # noqa: RUF012

    def scope_published(query):
        return query.where("published", True)

    @relation
    def author(self):
        from app.models.user import User

        return self.belongs_to(User)

    @relation
    def comments(self):
        from app.models.comment import Comment

        return self.morph_many(Comment, "commentable")
