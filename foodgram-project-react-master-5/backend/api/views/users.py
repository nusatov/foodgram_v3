from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from api.serializers.users import (FollowerSerializer, SubscriptionSerializer,
                                   UserReadSerializer)
from users.models import Subscription, User


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = LimitPageNumberPagination
    
    def get_permissions(self):
        if self.action in ('me',):
            self.permission_classes = (IsAuthenticated, )
        return super().get_permissions()
    
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
            serializer = FollowerSerializer(data={'follower': user.id, 'author': author.id},
                                            context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # delete
        subscriptions_deleted, _ = Subscription.objects.filter(
            follower=user,
            author=get_object_or_404(User, pk=id)
        ).delete()
        if not subscriptions_deleted:
            return Response({'error': 'Подписка не найдена'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='subscriptions', permission_classes=(IsAuthenticated,))
    def user_subscriptions(self, request):
        user = request.user
        
        authors = User.objects.filter(following__follower=user)
        page = self.paginate_queryset(authors)
        
        context = {'request': request, 'is_subscription_request': True}
        
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)
        
