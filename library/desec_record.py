from ansible.module_utils.basic import *
import desec

def main():
    module = AnsibleModule(argument_spec={
        'domain': {
            'type': 'str',
            'required': True,
        },
        'subname': {
            'type': 'str',
            'required': True,
        },
        'type': {
            'type': 'str',
            'required': True,
        },
        'ttl': {
            'type': 'int',
            'required': True,
        },
        'records': {
            'type': 'list',
            'objects': 'str',
            'required': True,
        },
        'solo': {
            'type': 'bool',
            'default': False,
        },
        'token':  {
            'type': 'str',
            'required': True,
            'no_log': True
        }
    })

    client = desec.Client(token=module.params['token'])

    domain = module.params['domain']
    subname = module.params['subname']
    type = module.params['type']
    ttl = module.params['ttl']
    records = module.params['records']
    solo = module.params['solo']
    state = "present"

    changed = False

    rrset = client.get_rrset(domain, subname, type)
    update = False

    if (state == 'present' and rrset != None):

        for record in records:
            if (record not in rrset.records):
                rrset.records.append(record)
                update = True

        for record in rrset.records:
            if (solo and record not in records):
                rrset.records.remove(record)
                update = True

        if (ttl != rrset.ttl):
            rrset.ttl = ttl
            update = True

        if (update):
            client.update_rrset(domain, rrset)
            changed = True

    if (state == 'present' and rrset == None):
        rrset = desec.models.RRSet(subname, type, ttl, records)
        client.create_rrset(domain, rrset)
        changed = True
         
    if (state == 'absent' and rrset != None):
        # TODO Delete
        pass

    module.exit_json(changed=changed, rrset=rrset.to_dict())

if __name__ == '__main__':
    main()