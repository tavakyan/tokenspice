from assets.netlists.oceanv4.models import btoken, datatoken, dtfactory
from assets.netlists.oceanv4.web3tools import web3util
from assets.netlists.oceanv4.web3tools.contract_base import ContractBase
from web3 import Web3

    
def test_ERC20(alice_wallet, alice_address,
               bob_wallet, bob_address):
    #use DTFactory to create the token, and Datatoken to mint it
    f = dtfactory.DTFactory()
    dt_address = f.createToken('', 'TOK', 'TOK', web3util.toBase18(100.0),
                               from_wallet=alice_wallet)
    dt = datatoken.Datatoken(dt_address)
    dt.mint(alice_address, web3util.toBase18(100.0), from_wallet=alice_wallet)

    #now that we've created & minted the token, we can use it with BToken interface
    token = btoken.BToken(dt_address)
    assert token.address == dt_address
    # import ipdb
    # ipdb.set_trace()
    # assert token.decimals() == 18
    assert token.balanceOf_base(alice_address) == web3util.toBase18(100.0)
    assert token.balanceOf_base(bob_address) == 0

    assert token.allowance_base(alice_address, bob_address) == 0
    token.approve(bob_address, int(1e18), from_wallet=alice_wallet)
    assert token.allowance_base(alice_address, bob_address) == int(1e18)

    #alice sends all her tokens to Bob, then Bob sends it back
    alice_TOK = token.balanceOf_base(alice_address)
    bob_TOK = token.balanceOf_base(bob_address)
    token.transfer(bob_address, alice_TOK, from_wallet=alice_wallet)
    assert token.balanceOf_base(alice_address) == 0
    assert token.balanceOf_base(bob_address) == (alice_TOK+bob_TOK)
    
    token.transfer(alice_address, alice_TOK, from_wallet=bob_wallet)
    assert token.balanceOf_base(alice_address) == alice_TOK
    assert token.balanceOf_base(bob_address) == bob_TOK

def test_OCEAN(OCEAN_address):
    # token = btoken.BToken(web3 = Web3(), address=OCEAN_address)
    token = btoken.BToken(contract_address=OCEAN_address)
    # import ipdb
    # ipdb.set_trace()

    assert token.symbol() == 'Ocean'
