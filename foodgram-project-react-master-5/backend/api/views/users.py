from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination

from users.models import Subscription, User
from api.serializers.users import UserReadSerializer, SubscriptionSerializer, FollowerSerializer


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get_current_user'):
            return UserReadSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user

        if request.method == 'POST':
            author = get_object_or_404(User, id=id)
            serializer = FollowerSerializer(data={'follower': user.id, 'author': author.id}, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # delete
        subscription = Subscription.objects.filter(
            follower=user,
            author=get_object_or_404(User, pk=id)
        )
        if not subscription.exists():
            return Response({'error': 'Подписка не найдена'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=(IsAuthenticated,))
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
            serializer = SubscriptionSerializer(
                [subscription.author for subscription in page],
                many=True,
                context=context
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            [subscription.author for subscription in subscriptions],
            many=True,
            context=context
        )
        return Response(serializer.data)
