from datetime import (
    datetime,
    timedelta,
    timezone,
)
import json

from django.test import (
    Client,
    TestCase,
)

from rules.models import (
    Rule,
)


class ViewsTestCase(TestCase):

    def setUp(self):
        self.rule = Rule()
        now = datetime.now(timezone.utc)
        self.rule.populate({
            'policy': 'block',
            'environment': 'prod',
            'surt': 'https://(org,archive,',
            'capture_date': {
                'start': now.isoformat(),
                'end': (now + timedelta(days=365)).isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': (now + timedelta(days=365)).isoformat(),
            },
            'seconds_since_capture': 256,
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': True,
        })
        self.rule.save()
        self.client = Client()

    def test_rules_get_surt_exact(self):
        response = self.client.get(
            '/rules', {'surt-exact': 'https://(org,archive,'})
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        self.assertEqual(len(parsed['result']), 1)

    def test_rules_get_surt_starts_with(self):
        response = self.client.get(
            '/rules', {'surt-start': 'https://(org,archive,'})
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        for result in parsed['result']:
            self.assertEqual(
                result['surt'].startswith('https://(org,archive,'), True)

    def test_rules_get_all(self):
        response = self.client.get('/rules')
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        self.assertEqual(len(parsed['result']), Rule.objects.count())

    def test_rules_new_success(self):
        response = self.client.post(
            '/rules',
            content_type='application/json',
            data=json.dumps({
                'surt': 'http://(doctor,who,)/companions/rose',
                'enabled': False,
                'environment': 'prod',
                'policy': 'allow',
            }))
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        new_rule = Rule.objects.get(
            surt='http://(doctor,who,)/companions/rose')
        self.assertEqual(new_rule.policy, 'allow')

    def test_rules_new_fail_json(self):
        response = self.client.post('/rules', {'bad': 'wolf'})
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(parsed['message'], 'unable to marshal json')

    def test_rules_new_fail_validation(self):
        response = self.client.post(
            '/rules',
            content_type='application/json',
            data=json.dumps({'bad': 'wolf'}))
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(parsed['message'], 'error validating json')

    def test_rule_get_success(self):
        response = self.client.get('/rule/1')
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        self.assertEqual(parsed['result']['id'], 1)

    def test_rule_update_success(self):
        response1 = self.client.get('/rule/1')
        self.assertEqual(response1.status_code, 200)
        parsed = json.loads(response1.content.decode('utf-8'))
        payload = dict(parsed['result'])
        payload['public_comment'] = 'UPDATE'
        response2 = self.client.put(
            '/rule/1',
            content_type='application/json',
            data=json.dumps(payload))
        self.assertEqual(response2.status_code, 200)
        update = json.loads(response2.content.decode('utf-8'))
        self.assertEqual(update['result']['rule']['public_comment'], 'UPDATE')
        self.assertEqual(
            update['result']['change']['rule'],
            parsed['result'])

    def test_rule_update_fail_json(self):
        response = self.client.put('/rule/1', {'bad': 'wolf'})
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(parsed['message'], 'unable to marshal json')

    def test_rule_update_fail_validation(self):
        response = self.client.put(
            '/rule/1',
            content_type='application/json',
            data=json.dumps({'bad': 'wolf'}))
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(parsed['message'], 'error validating json')

    def test_rule_delete(self):
        response = self.client.delete('/rule/1')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/rule/1')
        self.assertEqual(response.status_code, 404)

    def test_tree_for_surt(self):
        response = self.client.get('/rules/tree/https://(org,archive,')
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        self.assertEqual(len(parsed['result']) >= 1, True)

    def test_rules_for_request_success(self):
        response = self.client.get(
            '/rules/for-request',
            {
                'surt': 'https://(org,archive,',
                'capture-date': datetime.now(timezone.utc),
            })
        self.assertEqual(response.status_code, 200)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['message'], 'ok')
        self.assertEqual(len(parsed['result']) >= 1, True)

    def test_rules_for_request_missing_params(self):
        response = self.client.get(
            '/rules/for-request',
            {
                'capture-date': datetime.now(timezone.utc),
            })
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(
            parsed['message'], 'surt query string param is required')

    def test_rules_for_request_malformed_date(self):
        response = self.client.get(
            '/rules/for-request',
            {
                'surt': 'https://(org,archive,',
                'capture-date': 'bad-wolf',
            })
        self.assertEqual(response.status_code, 400)
        parsed = json.loads(response.content.decode('utf-8'))
        self.assertEqual(parsed['status'], 'error')
        self.assertEqual(
            parsed['message'], 'capture-date query string param must be '
            'a datetime')
