from xml.etree import ElementTree

from django.core.management.base import BaseCommand

from rules.models import Rule


POLICY_MAP = {
    'allow': 'allow',
    'block': 'block',
    'block-message': 'message',
}


class Command(BaseCommand):
    help = 'Generate rule data from an XML in-file'

    def add_arguments(self, parser):
        parser.add_argument('rule_file', nargs='+', type=str)
        parser.add_argument('fuzz', action='store_true')

    def handle(self, *args, **kwargs):
        for infile in kwargs['rule_file']:
            tree = ElementTree.parse(infile)
            root = tree.getroot()

            for rule_xml in root.iter('rule'):
                policy = rule_xml.find('policy').text
                policy_value = POLICY_MAP.get(policy, 'rewrite-js')
                surt = rule_xml.find('surt').text
                who = rule_xml.find('who').text
                who = who if who else ''
                exact_match = rule_xml.find('exactMatch').text == 'true'
                rule = Rule(
                    policy=policy_value,
                    surt=surt,
                    js_modifications=
                        policy if policy_value == 'rewrite-js' and policy
                        else '',
                    who=who,
                    exact_match=exact_match,
                    enabled=True)
                # if kwargs['fuzz']:
                # Fuzz values for rule data here
                rule.save()
