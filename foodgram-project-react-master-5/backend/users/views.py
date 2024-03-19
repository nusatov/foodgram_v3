from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from foodgram_backend.pagination import LimitPageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import UserFollowSerializer, UserReadSerializer


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserFollowSerializer
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action in ('get_current_user',):
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get_current_user'):
            return UserReadSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response({'error': 'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Subscription.objects.filter(
                    follower=user,
                    author=author
            ).exists():
                return Response({'error': 'Вы уже подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(follower=user, author=author)
            recipes_limit = request.query_params.get('recipes_limit')

            try:
                recipes_limit = (
                    int(recipes_limit) if recipes_limit is not None else None
                )
            except ValueError:
                return Response(
                    {'error': 'Неверный формат для параметра recipes_limit'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            context = {'request': request, 'recipes_limit': recipes_limit,
                       'is_subscription_request': True}
            serializer = self.get_serializer(author, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                follower=user,
                author=author
            )
            if not subscription.exists():
                return Response({'error': 'Подписка не найдена'},
                                status=status.HTTP_400_BAD_REQUEST
                                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def user_subscriptions(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Пользователь не авторизован'},
                            status=status.HTTP_401_UNAUTHORIZED
                            )

        subscriptions = Subscription.objects.filter(
            follower=user
        ).select_related('author')
        page = self.paginate_queryset(subscriptions)

        context = {'request': request, 'is_subscription_request': True}
        if 'recipes_limit' in request.query_params:
            context['recipes_limit'] = int(
                request.query_params.get('recipes_limit')
            )

        if page is not None:
            serializer = UserFollowSerializer(
                [subscription.author for subscription in page],
                many=True,
                context=context
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserFollowSerializer(
            [subscription.author for subscription in subscriptions],
            many=True,
            context=context
        )
        return Response(serializer.data)
