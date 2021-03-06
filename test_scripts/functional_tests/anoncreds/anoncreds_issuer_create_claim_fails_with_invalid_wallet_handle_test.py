"""
Created on Dec 19, 2017

@author: nhan.nguyen
Verify that user cannot create claim with invalid wallet handle.
"""
import json

from indy import anoncreds
from indy.error import ErrorCode
import pytest

from test_scripts.functional_tests.anoncreds.anoncreds_test_base \
    import AnoncredsTestBase
from utilities import utils, common, constant


class TestIssuerCreateClaimWithInvalidWalletHandle(AnoncredsTestBase):

    @pytest.mark.asyncio
    async def test(self):
        # 1. Create wallet.
        # 2. Open wallet.
        self.wallet_handle = await common.create_and_open_wallet_for_steps(
            self.steps, self.wallet_name, self.pool_name)

        # 3. Create 'issuer_did'.
        # 4. Create 'prover_did'.
        ((issuer_did, _),
         (prover_did, _)) = await common.create_and_store_dids_and_verkeys(
            self.steps, self.wallet_handle, number=2,
            step_descriptions=["Create 'issuer_did'", "Create 'prover_did'"])

        # 5. Create master secret.
        self.steps.add_step("Create master secret")
        await utils.perform(self.steps, anoncreds.prover_create_master_secret,
                            self.wallet_handle, constant.secret_name)

        # 6. Create and store claim definition.
        self.steps.add_step("Create and store claim definition")
        claim_def = await utils.perform(
            self.steps, anoncreds.issuer_create_and_store_claim_def,
            self.wallet_handle, issuer_did, json.dumps(constant.gvt_schema),
            constant.signature_type, False)

        # 7. Create claim request.
        self.steps.add_step("Create claim request")
        claim_offer = utils.create_claim_offer(issuer_did,
                                               constant.gvt_schema_seq)
        claim_req = await utils.perform(
            self.steps, anoncreds.prover_create_and_store_claim_req,
            self.wallet_handle, prover_did, json.dumps(claim_offer), claim_def,
            constant.secret_name)

        # 8. Create claim with invalid wallet handle and verify that
        # user cannot create claim.
        self.steps.add_step("Create claim with invalid wallet handle"
                            " and verify that user cannot create claim")
        error_code = ErrorCode.WalletInvalidHandle
        await utils.perform_with_expected_code(self.steps,
                                               anoncreds.issuer_create_claim,
                                               self.wallet_handle + 1,
                                               claim_req,
                                               json.dumps(constant.xyz_claim),
                                               -1, expected_code=error_code)
