from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from api.serializers import CommentSerializer, GroupSerializer, PostSerializers
from posts.models import Group, Post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializers

    def perform_create(self, serializer):
        """Сохраняет автора поста(авториз.пользователь)"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Запрещает редактировать не автору"""
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение не своего контента недопустимо')
        return super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        """Запрещает удалять не автору"""
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление не своего контента недопустимо')
        instance.delete()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Возвращает запрос, отфильтрованный по id"""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post.comments

    def perform_create(self, serializer):
        '''Сохраняет автора коммента'''
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        """Запрещает редактировать не автору"""
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента не допустимо')
        super(CommentViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление контента не допустимо')
        instance.delete()
