from ads.api import adwords
from base import utils


class SyncManager(object):
    """Sync different things related to the client"""

    def all(self):
        # TODO handle it in another way
        from .models import Client
        """Update list of all clients from AdWords"""
        api = adwords.API()
        selector = {'fields': ['CustomerId', 'Name']}
        mcs = api.client.GetService('ManagedCustomerService',
                                    version=api.VERSION)
        clients_raw = mcs.get(selector)

        # Data structure that holds data for master-client
        data = {}

        # Fill with name, customer id
        # TODO make a separate method
        for item in clients_raw.entries:
            unique_id = utils.unique_id_dashed(item.customerId)
            data[item.customerId] = {'name': item.name, 'id': unique_id}

        # Fill with master
        # TODO make a separate method
        if hasattr(clients_raw, 'links'):
            for item in clients_raw.links:
                manager_id = utils.unique_id_dashed(item.managerCustomerId)
                data[item.clientCustomerId]['master'] = manager_id


        # TODO improve with generators
        # TODO make a separate method
        for key in data.keys():

            params = {
                'adwords_id': data[key]['id'],
                'name': data[key]['name'],
            }

            if not Client.objects.filter(
                    adwords_id=params['adwords_id']).exists():
                Client.objects.get_or_create(**params)

        # TODO move to separate method
        # TODO use list comprehensions or generators
        for key in data.keys():
            master_id = data[key].get('master')
            if master_id:
                client_id = data[key]['id']
                master = Client.objects.get(adwords_id=master_id)
                client = Client.objects.get(adwords_id=client_id)
                client.master = master
                client.save()

        # TODO check the case when client is empty (maybe the client has gone)
        # Client.objects.filter(name='').delete()
