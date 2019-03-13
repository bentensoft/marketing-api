from .models import Client
from rest_framework import serializers


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    ads = serializers.SerializerMethodField()
    onboarding = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    def get_onboarding(self, obj):
        return obj.onboarding_percent_completed()

    def get_tasks(self, obj):
        # return obj.tasks.filter(is_done=False).count()
        return 0

    def get_logo(self, obj):
        if obj.logo:
            return 'https://api.yaelconsulting.com%s' % obj.logo.url
        return ''

    def get_ads(self, obj):
        kwargs = {}
        if all([
            self.context.get('created__month'),
            self.context.get('created__year')
        ]):
            kwargs = {
                'created__month': self.context.get('created__month'),
                'created__year': self.context.get('created__year')
            }
        ad = obj.ads.filter(**kwargs).first()
        if ad:
            return {
                'adwords': ad.adwords,
                'bingads': ad.bingads,
                'facebookads': ad.facebookads
            }
        return {}

    class Meta:
        model = Client
        fields = ('id', 'name', 'ads', 'onboarding', 'tasks', 'logo')
        depth = 1


class MasterSerializer(serializers.HyperlinkedModelSerializer):
    clients = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('id', 'name', 'clients')
        depth = 1

    def get_clients(self, master):
        to_exclude = ['MHI - MCC', 'Joe - NYC Focus',
                      'Johnson Development MCC']
        clients = master.clients.exclude(name__in=to_exclude)\
                                .filter(is_enabled=True)
        if self.context['request'].user.username == 'facebookuser':
            clients = clients.filter(name='Yael Consulting')
        serializer = ClientSerializer(instance=clients, many=True,
                                      context=self.context)
        return serializer.data


class ClientDetailSerializer(serializers.HyperlinkedModelSerializer):
    ads = serializers.SerializerMethodField()
    onboarding = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    def get_logo(self, obj):
        if obj.logo:
            return 'https://api.yaelconsulting.com%s' % obj.logo.url
        return None

    def get_onboarding(self, obj):
        return obj.onboarding_percent_completed()

    def get_ads(self, obj):
        kwargs = {}
        if all([
            self.context.get('created__month'),
            self.context.get('created__year')
        ]):
            kwargs = {
                'created__month': self.context.get('created__month'),
                'created__year': self.context.get('created__year')
            }
        ad = obj.ads.filter(**kwargs).first()
        if ad:
            return {
                'adwords': ad.adwords,
                'bingads': ad.bingads,
                'facebookads': ad.facebookads
            }
        return {}

    class Meta:
        model = Client
        read_only_fields = ('id', 'name', 'adwords_id',)
        fields = (
            'id', 'name', 'is_custom', 'is_enabled', 'onboarding', 'logo',
            'adwords_id', 'planned_budget_adwords', 'planned_cpa_adwords',
            'planned_conversions_adwords',

            'bingads_id', 'planned_budget_bingads', 'planned_cpa_bingads',
            'planned_conversions_bingads',

            'facebookads_id', 'planned_budget_facebookads',
            'planned_cpa_facebookads', 'planned_conversions_facebookads', 'ads'
        )


class ClientCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Client
        fields = (
            'id', 'name', 'is_custom', 'google_spreadsheet',
            'adwords_id', 'planned_budget_adwords', 'planned_cpa_adwords',
            'planned_conversions_adwords',

            'bingads_id', 'planned_budget_bingads', 'planned_cpa_bingads',
            'planned_conversions_bingads',

            'facebookads_id', 'planned_budget_facebookads',
            'planned_cpa_facebookads', 'planned_conversions_facebookads',
        )

    def create(self, validated_data):
        validated_data['is_custom'] = True
        validated_data['is_enabled'] = True
        return super().create(validated_data)


class ClientIDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ('id',)
