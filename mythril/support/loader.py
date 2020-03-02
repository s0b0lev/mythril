"""This module contains the dynamic loader logic to get on-chain storage data
and dependencies."""
from mythril.disassembler.disassembly import Disassembly
import logging
import re
import functools
from mythril.ethereum.interface.rpc.client import EthJsonRpc
from typing import Optional

LRU_CACHE_SIZE = 4096

log = logging.getLogger(__name__)


class DynLoader:
    """The dynamic loader class."""

    def __init__(self, eth: Optional[EthJsonRpc], active=True):
        """

        :param eth:
        :param active:
        """
        self.eth = eth
        self.active = active

    @functools.lru_cache(LRU_CACHE_SIZE)
    def read_storage(self, contract_address: str, index: int) -> str:
        """

        :param contract_address:
        :param index:
        :return:
        """
        if not self.active:
            raise ValueError("Loader is disabled")
        if not self.eth:
            raise ValueError("Cannot load from the storage when eth is None")

        return self.eth.eth_getStorageAt(
            contract_address, position=index, block="latest"
        )

    @functools.lru_cache(LRU_CACHE_SIZE)
    def read_balance(self, address: str) -> str:
        """

        :param address:
        :return:
        """
        if not self.active:
            raise ValueError(
                "Cannot load from storage when the loader is disabled"
            )
        if not self.eth:
            raise ValueError("Cannot load from the storage when eth is None")

        return self.eth.eth_getBalance(address)

    @functools.lru_cache(LRU_CACHE_SIZE)
    def dynld(self, dependency_address: str) -> Optional[Disassembly]:
        """
        :param dependency_address:
        :return:
        """
        if not self.active:
            raise ValueError("Loader is disabled")
        if not self.eth:
            raise ValueError("Cannot load from the storage when eth is None")

        log.debug("Dynld at contract %s", dependency_address)

        # Ensure that dependency_address is the correct length, with 0s prepended as needed.
        dependency_address = (
            "0x" + "0" * (42 - len(dependency_address)) + dependency_address[2:]
        )

        m = re.match(r"^(0x[0-9a-fA-F]{40})$", dependency_address)

        if m:
            dependency_address = m.group(1)

        else:
            return None

        log.debug("Dependency address: %s", dependency_address)

        code = self.eth.eth_getCode(dependency_address)

        if code == "0x":
            return None
        else:
            return Disassembly(code)
