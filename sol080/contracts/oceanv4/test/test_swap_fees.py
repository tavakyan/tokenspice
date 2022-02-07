import brownie

from sol080.contracts.oceanv4 import oceanv4util
from util.base18 import toBase18
from util.constants import BROWNIE_PROJECT080, OPF_ACCOUNT, GOD_ACCOUNT
from util.globaltokens import OCEANtoken
from util.globaltokens import fundOCEANFromAbove


GOD_ADDRESS = GOD_ACCOUNT.address
OPF_ADDRESS = OPF_ACCOUNT.address

accounts = brownie.network.accounts

account0 = accounts[0]
address0 = account0.address

account1 = accounts[1]
address1 = account1.address


def test_exactAmountIn_fee():
    pool = _deployBPool()
    OCEAN = OCEANtoken()
    fundOCEANFromAbove(address0, toBase18(10000))
    OCEAN.approve(pool.address, toBase18(10000), {"from": account0})
    datatoken = BROWNIE_PROJECT080.ERC20Template.at(pool.getDataTokenAddress())

    assert datatoken.balanceOf(address0) == 0
    account0_DT_balance = datatoken.balanceOf(address0)
    account0_Ocean_balance = OCEAN.balanceOf(address0)
    oceanMarketFeeBal = pool.publishMarketFees(OCEAN.address)

    tokenInOutMarket = [OCEAN.address, datatoken.address, address1]
    # [tokenIn,tokenOut,marketFeeAddress]
    amountsInOutMaxFee = [toBase18(100), toBase18(1), toBase18(100), toBase18(0.001)]
    # [exactAmountIn,minAmountOut,maxPrice,_swapMarketFee=0.1%]

    tx = pool.swapExactAmountIn(
        tokenInOutMarket, amountsInOutMaxFee, {"from": account0}
    )
    assert datatoken.balanceOf(address0) > 0

    assert tx.events["SWAP_FEES"][0]["marketFeeAmount"] == toBase18(
        0.01 * 100
    )  # 0.01: mkt_swap_fee in oceanv4util.create_BPool_from_datatoken, 100: exactAmountIn
    assert tx.events["SWAP_FEES"][0]["tokenFees"] == OCEAN.address
    assert oceanMarketFeeBal + tx.events["SWAP_FEES"][0][
        "marketFeeAmount"
    ] == pool.publishMarketFees(tx.events["SWAP_FEES"][0]["tokenFees"])

    # account1 received fee
    assert OCEAN.balanceOf(address1) == toBase18(0.001 * 100)

    # account0 ocean balance decreased
    assert (
        OCEAN.balanceOf(address0) + tx.events["LOG_SWAP"][0]["tokenAmountIn"]
        == account0_Ocean_balance
    )

    # account0 DT balance increased
    assert account0_DT_balance + tx.events["LOG_SWAP"][0][
        "tokenAmountOut"
    ] == datatoken.balanceOf(address0)


# def test_vesting_available():
#     pool = _deployBPool()
#     OCEAN = OCEANtoken()
#     fundOCEANFromAbove(address1, toBase18(100000))
#     OCEAN.approve(pool.address, toBase18(100000), {"from": account1})
#     datatoken = BROWNIE_PROJECT080.ERC20Template.at(pool.getDataTokenAddress())

#     sideStakingAddress = pool.getController()
#     sideStaking = BROWNIE_PROJECT080.SideStaking.at(sideStakingAddress)
    
#     ssContractDTbalance = datatoken.balanceOf(sideStaking.address)
#     ssContractBPTbalance = pool.balanceOf(sideStaking.address)

#     assert datatoken.balanceOf(address1) == 0

#     OceanAmountIn = toBase18(50000) # try amount big enough so that the staking contract won't stake
#     minBPTOut = toBase18(0.001)

#     # try:
#     receipt = pool.joinswapExternAmountIn(
#         OCEAN.address,
#         OceanAmountIn,
#         minBPTOut,
#         {"from": account1}
#     )
#     # except:
#     #     brownie.exceptions.VirtualMachineError

#     assert datatoken.balanceOf(address1) == 0

def _deployBPool():
    brownie.chain.reset()
    router = oceanv4util.deployRouter(account0)
    fundOCEANFromAbove(address0, toBase18(100000))
    createdDataNFT = oceanv4util.createDataNFT(
        "dataNFT", "DATANFTSYMBOL", account0, router
    )
    dataNFT = createdDataNFT[0]
    datatoken = oceanv4util.createDatatokenFromDataNFT(
        "DT", "DTSYMBOL", 10000, dataNFT, account0
    )
    erc721_factory = createdDataNFT[1]
    pool = oceanv4util.createBPoolFromDatatoken(
        datatoken, 1000, 80000, account0, erc721_factory
    )
    return pool