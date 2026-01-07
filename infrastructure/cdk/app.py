#!/usr/bin/env python3
"""
AWS CDK App for Cantonese Word Game Infrastructure
"""
import aws_cdk as cdk
from cantonese_word_game_stack import CantoneseWordGameStack

app = cdk.App()
CantoneseWordGameStack(
    app,
    "CantoneseWordGameStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account") or None,
        region=app.node.try_get_context("region") or "us-east-1",
    ),
    description="Infrastructure for Cantonese Word Game application",
)

app.synth()

