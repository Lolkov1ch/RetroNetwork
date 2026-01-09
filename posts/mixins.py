from django.core.exceptions import PermissionDenied


class UserIsOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not getattr(request.user, "is_authenticated", False) or getattr(obj, "creator", None) != request.user:
            raise PermissionDenied("You don't have permission to edit this post.")
        return super().dispatch(request, *args, **kwargs)
