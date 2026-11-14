# Рецепт: новая фича от таблицы до экрана

Пример: посты пользователя (создать, список своих, удалить). Порядок снизу вверх, после каждого
шага проект собирается. В каждом слое появляется зона `posts`.

## 1. Домен: `app/domain/posts/`

```python
# models.py
@dataclass(frozen=True, slots=True)
class PostInfo:
    id: UUID
    author_id: UUID
    title: str
    body: str
    created_at: datetime

# errors.py
class PostNotFoundError(NotFoundError):
    error_code = ErrorCode.POST_NOT_FOUND          # добавить значение в core/errors.py::ErrorCode
    default_detail = "Post not found"

# rules.py
def ensure_can_delete(actor: CurrentUser, author_id: UUID) -> None:
    # POSTS_MODERATE добавить в Permission; у admin оно появится само (frozenset(Permission))
    if actor.id != author_id and not actor.can(Permission.POSTS_MODERATE):
        raise ForbiddenError()
```

`__init__.py` реэкспортирует `PostInfo`, `PostNotFoundError`, `ensure_can_delete` через `__all__`.

## 2. Таблица и миграция

`app/db/models/posts.py`, импорт в `db/models/__init__.py`, затем `make migration m="add posts"` и
чтение получившегося файла глазами.

```python
class Post(UuidPkMixin, TimestampMixin, Base):
    __tablename__ = "posts"

    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)

    __table_args__ = (Index("ix_posts_author_created", "author_id", "created_at"),)
```

## 3. Репозиторий

`app/db/repositories/posts.py`, подключить в `db/uow.py` как `self.posts`. Весь SQL живёт здесь,
сервис не видит SQLAlchemy.

```python
class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, post: Post) -> None:
        self._session.add(post)

    async def get(self, post_id: UUID) -> Post | None:
        return await self._session.get(Post, post_id)

    async def delete(self, post: Post) -> None:
        await self._session.delete(post)

    async def by_author(self, author_id: UUID, *, limit: int) -> Sequence[Post]:
        stmt = select(Post).where(Post.author_id == author_id).order_by(Post.created_at.desc()).limit(limit)
        return (await self._session.scalars(stmt)).all()
```

## 4. Сервис: `app/service/posts/`

Возвращает доменные объекты, не коммитит, внешний мир получает через порты.

```python
class PostService:
    def __init__(self, uow: UnitOfWork, actor: CurrentUser) -> None:
        self._uow = uow
        self._actor = actor

    async def create(self, title: str, body: str) -> PostInfo:
        post = Post(author_id=self._actor.id, title=title, body=body)
        self._uow.posts.add(post)
        await self._uow.flush()
        return to_info(post)            # маппер ORM -> PostInfo в service/posts/mappers.py

    async def delete(self, post_id: UUID) -> None:
        post = await self._uow.posts.get(post_id)
        if post is None:
            raise PostNotFoundError()
        ensure_can_delete(self._actor, post.author_id)
        await self._uow.posts.delete(post)
```

## 5. API: `app/api/v1/posts/`

```text
api/v1/posts/
  __init__.py   router = APIRouter(prefix="/posts", tags=["Posts"]); include_router(...)
  posts.py      эндпоинты
  schemas.py    PostCreate, PostOut
  deps.py       PostServiceDep
```

```python
# deps.py
def _post_service(uow: UowDep, actor: CurrentUserDep) -> PostService:
    return PostService(uow, actor)

PostServiceDep = Annotated[PostService, Depends(_post_service)]

# posts.py
@router.post(path="", status_code=201, summary="Create a post")
async def create_post(payload: PostCreate, svc: PostServiceDep) -> PostOut:
    return PostOut.from_domain(await svc.create(payload.title, payload.body))
```

Подключить группу в `api/v1/__init__.py`: `router.include_router(posts.router)`.

## 6. Тесты

- unit: `tests/unit/domain/test_posts.py` на `ensure_can_delete`;
- integration: `tests/integration/api/test_posts.py`: создал, вижу в списке, чужой удалить не
  может (403), свой удалил, повторное удаление даёт 404 `POST_NOT_FOUND`.

## 7. Фронтенд

1. `make openapi`: обновит `frontend/openapi.json` и типы в `src/shared/api/schema.d.ts`.
2. `entities/post`: типы UI-модели, маппер из `Schemas["PostOut"]`, API-функции, `postKeys`, хуки
   запросов.
3. `features/create-post`, `features/delete-post`: мутации и формы, инвалидация `postKeys`.
4. `widgets/post-list` при необходимости, `_pages/posts`, маршрут `app/(app)/posts/page.tsx`.
5. Ссылка в `widgets/app-header`. Подробнее: [frontend/architecture.md](../frontend/architecture.md).

## Перед коммитом

`make check` зелёный (сюда входят import-linter и steiger). Миграция прочитана, у неё есть
`downgrade()`. Если фича меняет контракт или принято решение, запись в `docs/DECISIONS.md`.
