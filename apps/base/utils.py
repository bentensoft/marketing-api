def unique_id_dashed(unique_id):
    """xxxxxxxxxx -> xxx-xxx-xxxx (used in CRM)"""
    suid = str(unique_id)
    return '%s-%s-%s' % (suid[:3], suid[3:6], suid[6:])


def unique_id_serialize(unique_id):
    """xxx-xxx-xxxx -> xxxxxxxxxx (used by AdWords API)"""
    return int(''.join(unique_id.split('-')))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
