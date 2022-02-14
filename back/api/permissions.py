from rest_framework import permissions


class CreateOrConfirmOrLoginOrIsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        return view.action in ('create', 'confirm', 'login')
