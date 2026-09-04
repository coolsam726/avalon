"""ORM tour — one JSON map of M5 features exercised by this app."""

from __future__ import annotations

from app.models.post import Post
from app.models.user import User
from app.support.demo_db import ensure_demo_database
from avalon.http import Controller


class OrmTourController(Controller):
    async def index(self) -> dict:
        await ensure_demo_database()
        published = await Post.query().published().with_("author").get()
        page = await Post.query().published().order_by("id").paginate(1, page=1)
        trashed = await Post.only_trashed().count()
        authors = await User.query().has("posts", ">=", 1).with_count("posts").get()
        with_roles = await User.query().with_("roles").first()
        return {
            "features": {
                "eager_load": {
                    "endpoint": "GET /api/posts",
                    "count": len(published),
                    "sample_author": published[0].author.email if published else None,
                },
                "local_scope": {
                    "endpoint": "GET /api/posts",
                    "scope": "published()",
                    "published_titles": [post.title for post in published],
                },
                "pagination": {
                    "endpoint": "GET /api/posts/pages?page=1&per_page=1",
                    "page": page.to_dict(),
                },
                "soft_deletes": {
                    "endpoint": "GET /api/posts/trashed",
                    "trashed_count": trashed,
                },
                "with_count_and_where_has": {
                    "endpoint": "GET /api/users + /api/users/authors",
                    "authors": [
                        {
                            "email": user.email,
                            "posts_count": user._extra.get("posts_count", 0),
                        }
                        for user in authors
                    ],
                },
                "belongs_to_many_pivot": {
                    "endpoint": "GET /api/users",
                    "sample_roles": (
                        [
                            {
                                "name": role.name,
                                "pivot_level": role.get_raw_attribute("pivot_level"),
                            }
                            for role in with_roles.roles
                        ]
                        if with_roles and with_roles.relation_loaded("roles")
                        else []
                    ),
                },
                "morph_many": {
                    "endpoint": "GET /api/posts/1/comments",
                    "hint": "Seed attaches a comment to Ada's first post",
                },
                "upsert": {
                    "endpoint": "POST /api/users/upsert",
                    "body": {"email": "ada@avalon.dev", "name": "Ada Lovelace"},
                },
                "no_lazy_load": {
                    "endpoint": "GET /api/users/1/posts",
                    "contract": "Unloaded user.posts raises RelationNotLoadedError",
                },
            }
        }
