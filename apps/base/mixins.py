from rest_framework.permissions import IsAdminUser


class AdminPermission(object):
    permission_classes = [IsAdminUser]


class PaginationMixin(object):
    page_size = 100

    @property
    def page(self):
        try:
            return int(self.kwargs.get('page', '1'))
        except:
            return 1

    @property
    def page_first(self):
        return self.page_size * self.page - self.page_size

    @property
    def page_last(self):
        return self.page_size * self.page

    def get_queryset(self):
        qs = super().get_queryset()
        return qs[self.page_first:self.page_last]


# class FilterMixin(object):
#
#     def get_queryset_kwargs(self):
#         return
