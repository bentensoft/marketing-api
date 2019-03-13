from django.db.models import Q


class SearchParser(object):
    """
    Modifies queryset for the model to do complex search

    Recognizes:

    - just search text
    - "exact" search
    - exclude if -word
    """

    def __init__(self, model, initial, field, *args, **kwargs):
        self.model = model
        self.initial = initial.split(' ')
        self.field = field

    def exclude_items(self):
        items = filter(lambda x: x.startswith('-'), self.initial)
        return [item[1:] for item in items]

    def exact_items(self):
        items = filter(
            lambda x: any([x.startswith('"') and x.endswith('"'),
                           x.startswith("'") and x.endswith("'")]),
            self.initial
        )
        return [item.replace("'", "").replace('"', "") for item in items]

    def q(self):
        return ' '.join([item for item in self.initial if not any(
            [
                item.startswith('"') and item.endswith('"'),
                item.startswith("'") and item.endswith("'"),
                item.startswith('-')
            ])])

    def exclude(self):
        items = self.exclude_items()
        excludes = None
        for item in items:
            q = Q(**{'%s__icontains' % self.field: item})
            excludes = (excludes and (excludes | q)) or q
        return excludes

    def get_queryset(self, values=None, **kwargs):
        """
        composes queryset object with `values` fields. By default values is
        None that means we must omit it
        """

        [kwargs.update({'%s__contains' % self.field: item})
         for item in self.exact_items()]
        if self.initial:
            if not self.q() in [None,'']:
                kwargs.update({'%s__icontains' % self.field: self.q()})
        qs = self.model.objects
        excludes = self.exclude()
        if excludes:
            qs = qs.exclude(excludes)

        if values:
            qs = qs.values(*values)

        return qs.filter(**kwargs)
