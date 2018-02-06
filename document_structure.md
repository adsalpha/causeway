# Rein Document Format

## Explanations
1. The ID field in every job related document is the SHA256 hash of its **unencrypted** contents as JSON.

2. "" means data of type string. Further explanations and type specifications given when necessary.

3. Documents are first hashed to obtain the ID, then encrypted, then signed with Bitcoin. This way, the worker or the job creator could not alter the data while still having a valid signature. The signature is checked on server-side.

Every document includes the following field:
```
validity: {
  signature: "",
  signature_address: ""
}
```

4. The parent job field establishes a chain of immutability between the child and parent documents. It is encrypted altogether with the contents to ensure that the server can't move a document to a different job.

Job related documents include the following field:
```
job: {
  id: "",
  url: https://causeway-server.whatever/jobs/<JOB_ID>
}
```

5. Every job related document contains a time-related field represented as an `int` timestamp. It is encrypted altogether with the contents because it makes sense only if the contents are present.

6. Above certain fields there are notes enclosed in `<>`. They only refer to the field below unless otherwise specified.

## Client Generated

##### JOB
```
{
  id: "",
  type: job,
  time: {
    created_at: <>,
    bidding_closes_at: <>
  },
  name: "",
  description: "",
  tags: "",
  creator: {
    login: "",
    email: "",
    url: https://causeway-server.whatever/users/<SIN>
  },
  mediator: {
    login: "",
    email: "",
    fee: <float>,
    url: https://causeway-server.whatever/users/<SIN>
  }
}
```

##### BID
```
{
  id: "",
  type: bid,
  created_at: <>,
  worker: {
    name: "",
    email: "",
    url: https://causeway-server.whatever/users/<SIN>
  },
  amount: <float>,
  description: ""
}
```

##### OFFER
```
{
  id: "",
  type: offer,
  created_at: <>,
  bid_id: "",
  worker_escrow: {
    address: "",
    pubkey: "",
    redeem_script: "",
    tx_fee: <float>
  },
  mediator_escrow: {
    address: "",
    pubkey: "",
    redeem_script: "",
    tx_fee: <float>
  },
  creator_refund: {
    address: "",
    pubkey: ""
  }
}
```

##### DELIVERY
The `sig` field is an array of signatures. More than one is necessary with (m>2)-of-(n>3) multisig.

```
{
  id: "",
  type: delivery,
  created_at: <>,
  description: "",
  worker_payment: {
    inputs: "",
    address: "",
    amount: <float>,
    sig: ["", ""]
  },
  mediator_payment: {
    inputs: "",
    address: "",
    amount: <float>,
    sig: ["", ""]
  },
  <if worker_payment['amount'] != bid['amount']>
  creator_refund: {
    amount: <float>,
    txid: "",
    sig: ["", ""]
  } 
}
```

##### ACCEPT DELIVERY
```
{
  id: "",
  type: accept_delivery,
  created_at: <>,
  delivery/dispute: https://causeway-server.whatever/jobs/<JOB_ID>/deliveries/<DELIVERY_ID>,
  finish_job: <bool>,
  worker_txid: "",
  <if job['finished'] == False>
  creator_refund: {
    txid: "",
    sig: ["", ""]
  },
  mediator_payment: {
    txid: "",
    sig: ["", ""]
  }
}
```

##### DISPUTE
```
{
  id: "",
  type: dispute,
  created_at: <>,
  source: <worker/client>,
  description: ""
}
```

##### RESOLUTION
```
{
  id: "",
  type: dispute_resolution,
  dispute: https://causeway-server.whatever/jobs/<JOB_ID>/dispute/<DISPUTE_ID>,
  created_at: <>,
  finish_job: <bool>
  winner: <worker/client>,
  description: ""
}
```

##### ACCEPT DISPUTE RESOLUTION
If either the client or the worker wins the dispute, only one of the `worker_txid` or `creator_refund` fields is included. However, the mediator can decide to split the bid amount, and then the dispute resolution will contain both fields.

```
{
  id: "",
  type: accept_dispute_resolution,
  created_at: <>,
  delivery: https://causeway-server.whatever/jobs/<JOB_ID>/deliveries/<DELIVERY_ID>,
  dispute: https://causeway-server.whatever/jobs/<JOB_ID>/dispute/<DISPUTE_ID>,
  worker_txid: "",
  creator_refund: {
    amount: <float>,
    txid: "",
    sig: ["", ""]
  },
  mediator_payment: {
    txid: "",
    sig: ["", ""]
  }
}
```

##### USER
```
{
  id: "",
  type: user,
  created_at: <>,
  login: "",
  email: "",
  addresses: {
    master: "",
    delegate: ""
  }, 
  <if user mediates>
  mediator: {
    fee: <float>,
    pubkey: ""
  }
}
```

## Sent to Server

##### JOB & USER
Same as client generated.

##### JOB RELATED DOCUMENTS
```
{
  type: bid/offer/delivery/accept_delivery/dispute/dispute_resolution/accept_dispute_resolution,
  id: "",
  encrypted_contents: ""
}
```

## Server Stored

##### JOB
The server keeps all job related data encrypted in one monolithic document. It ensures that parts of the job are closely bonded, have a strong logical connection and shows which of them are present.

```
{
  id: "",
  name: "",
  description: "",
  tags: "",
  finished: <bool>,
  time: {
    created_at: <>,
    bidding_closes_at: <>
  },
  creator: {
    login: "",
    email: "",
    url: https://causeway-server.whatever/users/<SIN>
  },
  mediator: {
    login: "",
    email: "",
    fee: <float>,
    url: https://causeway-server.whatever/users/<SIN>
  },
  <everything below is added during the lifetime of the job>
  bids: [
    {
      id: "",
      encrypted_contents: "",
      <if bid is accepted>
      offer: {
        id: "",
        encrypted_contents: ""
      }
    },
    <another_bid>: {}
  ],
  deliveries: {
    id: "",
    encrypted_contents: "",
    <if delivery is accepted>
    accept_delivery: {
      id: "",
      encrypted_contents: ""
    }
  },
  disputes: {
    id: "",
    encrypted_contents: "",
    <if dispute is resolved>
    dispute_resolution: {
      id: "",
      encrypted_contents: ""
    }
    <if resolution is accepted>
    accept_dispute_resolution: {
      id: "",
      encrypted_contents: ""
    }
  }
}
```

##### USER
```
{
  login: "",
  created_at: <>,
  email: "",
  id: "",
  addresses: {
    master: "",
    delegate: "",
  }, 
  <if user mediates>
  mediator: {  
    fee: <float>,
    pubkey: ""
  },
  posted_jobs: [ <job id 1>, <job id 2>, <job id 3> ],
  rating: <computed at the time of request>
}
```

## Returned by Server

##### JOB & USER
Same as server stored.

##### BID
```
{
  type: bid,
  id: "",
  encrypted_contents: ""
  <if bid is accepted>
  offer: {
    id: "",
    created_at: <>,
    encrypted_contents: ""
  },
}
```

##### DELIVERY
```
{
  type: delivery,
  id: "",
  encrypted_contents: ""
  <if bid is accepted>
  accept_delivery: {
    id: "",
    created_at: <>,
    encrypted_contents: ""
  },
}
```

##### DISPUTE
```
{
  type: dispute,
  id: "",
  encrypted_contents: ""
  <if dispute is resolved>
  dispute_resolution: {
    id: "",
    created_at: <>,
    encrypted_contents: ""
  }
  <if resolution is accepted>
  accept_dispute_resolution: {
    id: "",
    created_at: <>,
    encrypted_contents: ""
  }
}
```
