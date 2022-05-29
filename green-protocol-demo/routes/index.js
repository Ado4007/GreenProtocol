var express = require('express');
var router = express.Router();
const nearAPI = require("near-api-js");
const {
    connect,
    keyStores,
    KeyPair,
    WalletConnection
} = nearAPI;

async function setupNear() {
    const keyStore = new keyStores.InMemoryKeyStore();
    const PRIVATE_KEY =
        "4pyMMGCCojhMzLCV59VtmJHLGRxyS7MnFyPJoJbbucxQmTuN7sL2DwCCFRceASUJg9BmC4QwiFoPbgysDMhAYxbf";
    // creates a public / private key pair using the provided private key
    const keyPair = KeyPair.fromString(PRIVATE_KEY);
    // adds the keyPair you created to keyStore
    await keyStore.setKey("testnet", "eu_authority.testnet", keyPair);
    const config = {
        networkId: "testnet",
        keyStore,
        nodeUrl: "https://rpc.testnet.near.org",
        walletUrl: "https://wallet.testnet.near.org",
        helperUrl: "https://helper.testnet.near.org",
        explorerUrl: "https://explorer.testnet.near.org",
    };
    const near = await connect(config);
    const account = await near.account("eu_authority.testnet");
    return account
}

async function nearFindContract(account) {
    account = await account
    const contract = new nearAPI.Contract(
        account, // the account object that is connecting
        "eu_authority.testnet", {
            // name of contract you're connecting to
            viewMethods: ["get_balance", "get_total_balance"], // view methods do not change state but usually return a value
            changeMethods: ["mint_new", "send_tokens"], // change methods modify state
            sender: account, // account object to initialize and sign transactions.
        }
    );
    return contract
}

async function setUp() {

    const account = await setupNear()
    const contract = await nearFindContract(account)

    return [account, contract]
}

/* GET home page. */
router.get('/', async function(req, res, next) {
    const [account, contract] = await setUp()
    const response = await contract.get_total_balance({
        "account": "eu_authority.testnet"
    });
    console.log(response)
    res.render('index', {
        title: 'Express'
    });
});

router.post('/gcp', async function(req, res, next) {
    const [account, contract] = await setUp()
    console.log(`[*] Minting new ${req.body.amount} tokens for ${req.body.accountId}`)
    await contract.mint_new({
        "receiver": req.body.accountId,
        "t_type": req.body.t_type,
        "amount": req.body.amount
    })
    res.json({
        "status": "ok"
    });
});

router.get('/gcp/:accountId', async function(req, res, next) {
    const [account, contract] = await setUp()
    const response = await contract.get_total_balance({
        "account": req.params.accountId
    });
    res.json(response)
});

router.post('/gcp/send', async function(req, res, next) {
    const [account, contract] = await setUp()
    //near call gcc.testnet send_tokens '{"receiver":"gcc.testnet", "t_types":[1], "amounts":[1]}' --accountId gcc1.testnet
    console.log(`[*] Transfering ${req.body.amounts[0]} tokens from spain1.testnet to gcp_exchange.testnet`)
    await contract.send_tokens({
        "receiver": req.body.accountId,
        "t_types": req.body.t_types,
        "amounts": req.body.amounts
    })
    res.json({
        "status": "ok"
    });
})

module.exports = router;