from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import (
    ChangePasswordSerializer, CustomUserCreateSerializer, CustomUserSerializer,
    SubscriptionSerializer)
from .models import Subscription

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet для кастомной модели User."""
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        print(self.action)
        if self.request.method in ('POST', 'PATCH'):
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        context = {'request': request}
        user = get_object_or_404(User, pk=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, context=context, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        author = get_object_or_404(User, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            Subscription.objects.create(author=author, user=user)
            serializer = CustomUserSerializer(author, context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Subscription, author=author, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
