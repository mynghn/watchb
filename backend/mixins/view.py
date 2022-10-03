from rest_framework.request import Request


class CollectUserFromRequestMixin:
    def initial(self, request: Request, *args, **kwargs):
        super(CollectUserFromRequestMixin, self).initial(request, *args, **kwargs)
        if "user" not in request.data.keys():
            request.data["user"] = request.user.pk
