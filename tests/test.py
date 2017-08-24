from time import sleep

from app.config.db import client, db
from tests.test_accept_delivery import TestAcceptDelivery
from tests.test_accept_dispute_resolution import TestAcceptDisputeResolution
from tests.test_bid import TestBid
from tests.test_delivery import TestDelivery
from tests.test_dispute import TestDispute
from tests.test_dispute_resolution import TestDisputeResolution
from tests.test_job import TestJob
from tests.test_offer import TestOffer
from tests.test_user import TestUser

client.drop_database(db)


george = TestUser(name='george')
assert george.send().status_code == 201
barbara = TestUser(name='barbara', mediator=True)
assert barbara.send().status_code == 201
print('Created ordinary users.')

john = TestUser(name='john', mediator=True)
assert john.send().status_code == 201
print('Created a mediator.')

assert john.send().status_code == 422
print('Verified user duplicate check.')

job1 = TestJob(name='Test how the new Causeway works',
               description='Write tests for http://github.com/ReinProject/causeway',
               tags=['tests', 'causeway'],
               creator=george,
               mediator=john)
assert job1.send().status_code == 201
print('Created a job.')

assert job1.send().status_code == 401
print('Verified nonce checking.')

job1.new_token()
assert job1.send().status_code == 422
print('Verified job duplicate check.')

bid1 = TestBid(description='I will write the tests for you.',
               worker=barbara,
               job=job1)
assert bid1.send().status_code == 201
print('Created a bid.')

bid1.new_token()
assert bid1.send().status_code == 422
print('Verified bid duplicate check.')

offer1 = TestOffer(bid=bid1)
assert offer1.send().status_code == 201
print('Offered to bid.')

offer1.new_token()
assert offer1.send().status_code == 422
print('Verified offer duplicate check.')

delivery1 = TestDelivery(description='https://github.com/barbara/dummy-causeway-tests',
                         job=job1,
                         worker=bid1.creator)
assert delivery1.send().status_code == 201
print('Delivered to job.')

delivery1.new_token()
assert delivery1.send().status_code == 422
print('Verified delivery duplicate check.')

accept_delivery1 = TestAcceptDelivery(delivery=delivery1)
assert accept_delivery1.send().status_code == 201
print('Accepted delivery.')

accept_delivery1.new_token()
assert accept_delivery1.send().status_code == 422
print('Verified accept delivery duplicate check.')

job2 = TestJob(name='Rewrite existing Rein client code to work with the new Causeway',
               description='Rewrite https://github.com/ReinProject/python-rein according to RDS v3',
               tags=['rein', 'specs'],
               creator=george,
               mediator=barbara)
assert job2.send().status_code == 201
print('Created a second job.')

bid2 = TestBid(description='I will rewrite the Rein client code.',
               worker=john,
               job=job2)
assert bid2.send().status_code == 201
print('Created a bid for the second job.')

offer2 = TestOffer(bid=bid2)
assert offer2.send().status_code == 201
print('Offered to the second job bid.')

dispute2 = TestDispute(description='No delivery from John.',
                       creator=george,
                       job=job2)
assert dispute2.send().status_code == 201
print('Disputed the second job.')

dispute2.new_token()
assert dispute2.send().status_code == 422
print('Verified dispute duplicate check.')

dispute_resolution2 = TestDisputeResolution(winner=george,
                                            description='No delivery from John.',
                                            dispute=dispute2)
assert dispute_resolution2.send().status_code == 201
print('Resolved the second job dispute.')

dispute_resolution2.new_token()
assert dispute_resolution2.send().status_code == 422
print('Verified dispute resolution duplicate check.')

accept_dispute_resolution2 = TestAcceptDisputeResolution(dispute=dispute2)
assert accept_dispute_resolution2.send().status_code == 201
print('Accepted the resolution for the second dispute.')

accept_dispute_resolution2.new_token()
assert accept_dispute_resolution2.send().status_code == 422
print('Verified accept dispute resolution duplicate check.')

print('\nPOST TESTS PASSED.\n')

jobs_get_active = TestJob.BulkQuery.get_active()
assert jobs_get_active.status_code == 200 and jobs_get_active.json() == []
print('Got active jobs.')

jobs_get_all = TestJob.BulkQuery.get_all()
jobs_get_all_json = jobs_get_all.json()
assert jobs_get_all.status_code == 200 and jobs_get_all_json[0]['id'] == job1['id'] and jobs_get_all_json[1]['id'] == job2['id']
print('Got all jobs.')

job1_get = TestJob.get(job1['id'])
assert job1_get.status_code == 200 and job1_get.json()['id'] == job1['id']
print('Got job 1.')

bid1_get = TestBid.get(job1['id'], bid1['id'])
assert bid1_get.status_code == 200 and bid1_get.json()['id'] == bid1['id']
print('Got bid for job 1.')

bid2_bulk_get = TestBid.BulkQuery.get(job2['id'])
assert bid2_bulk_get.status_code == 200 and bid2_bulk_get.json()[0]['id'] == bid2['id']
print('Got list of bids for job 2.')

delivery1_get = TestDelivery.get(job1['id'])
assert delivery1_get.status_code == 200 and delivery1_get.json()['id'] == delivery1['id']
print('Got delivery for job 1.')

dispute2_get = TestDispute.get(job2['id'])
assert dispute2_get.status_code == 200 and dispute2_get.json()['id'] == dispute2['id']
print('Got dispute for job 2.')

print('\nGET TESTS PASSED.\n')

print('Yaaaay! You can now push this build.')
