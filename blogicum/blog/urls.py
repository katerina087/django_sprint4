from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Главная страница
    path("", views.index, name="index"),

    # Публикации по категориям
    path("category/<slug:category_slug>/",
         views.category_posts,
         name="category_posts"),

    # Создание новой публикации
    path("posts/create/",
         views.create_post,
         name="create_post"),

    # Детальный просмотр публикации
    path("posts/<int:post_id>/",
         views.post_detail,
         name="post_detail"),

    # Редактирование публикации
    path("posts/<int:post_id>/edit/",
         views.edit_post,
         name="edit_post"),

    # Удаление публикации
    path("posts/<int:post_id>/delete/",
         views.delete_post,
         name="delete_post"),

    # Добавление комментария к публикации
    path("posts/<int:post_id>/comment/",
         views.add_comment,
         name="add_comment"),

    # Редактирование комментария
    path("posts/<int:post_id>/edit_comment/<int:comment_id>/",
         views.edit_comment,
         name="edit_comment"),

    # Удаление комментария
    path("posts/<int:post_id>/delete_comment/<int:comment_id>/",
         views.delete_comment,
         name="delete_comment"),

    # Редактирование своего профиля
    path("profile/edit/",
         views.edit_profile,
         name="edit_profile"),

    # Страница профиля пользователя
    path("profile/<str:username>/",
         views.profile,
         name="profile"),
]