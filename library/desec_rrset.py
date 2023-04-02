from ansible.module_utils.basic import *
import desec

DOCUMENTATION = r'''
author:
- Freerk-Ole Zakfeld (@fzakfeld)
description: Create, Update or Delete a DNS resource recordset
module: desec_rrset
options:
    token:
        description:
            - desec.io API token
        type: str
        required: true
    domain:
        description:
            - domain name of the DNS zone
        type: str
        required: true
    subname:
        description:
            - subname of the rrset
        type: str
        required: true
    type:
        description:
            - type of rrset (A, AAAA, TXT...)
        type: str
        required: true
    ttl:
        description:
            - Time-To-Live for the rrset
        type: int
        required: false
    solo:
        description:
            - Remove all other records that are not specified
        type: bool
        required: false
    records:
        description:
            - list of record values
        type: list
        objects: str
        required: false
'''

EXAMPLES = r'''
name: Create a AAAA recordset with 2 values
desec_record:
    domain: example.com
    token: xxxxx
    subname: www
    type: AAAA
    ttl: 3600
    solo: true
    records:
        - 2001:db8::100
        - 2001:db8::200
'''

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
            'required': False,
            'default': None,
        },
        'records': {
            'type': 'list',
            'objects': 'str',
            'required': False,
            'default': [],
        },
        'solo': {
            'type': 'bool',
            'required': False,
            'default': False,
        },
        'token':  {
            'type': 'str',
            'required': True,
            'no_log': True
        }
    }, supports_check_mode=True)

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

        if (ttl and ttl != rrset.ttl):
            rrset.ttl = ttl
            update = True

        if (update):
            if module.check_mode == False:
                client.update_rrset(domain, rrset)
            changed = True

    if (state == 'present' and rrset == None and len(records) > 0):
        rrset = desec.models.RRSet(subname, type, ttl or 3600, records)
        if module.check_mode == False:
            client.create_rrset(domain, rrset)
        changed = True
         
    if (state == 'absent' and rrset != None):
        # TODO Delete
        pass

    result = rrset.to_dict() if rrset else None

    module.exit_json(changed=changed, rrset=result)

if __name__ == '__main__':
    main()