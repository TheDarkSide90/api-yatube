from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from posts.models import Comment, Group, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly
    ]
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_queryset(self):
        post_id = self.get_post()
        new_queryset = Comment.objects.filter(post_id=post_id)
        return new_queryset

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(
            author=self.request.user,
            post=post
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        instance.delete()
