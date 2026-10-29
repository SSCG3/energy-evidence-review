# Security and configuration

This is a localhost prototype. Do not expose it as a production multi-user service. Document access labels and UI role selection are simulations, not identity authentication. Local request tokens and origin checks reduce cross-site misuse but do not replace an access-control deployment design.

Set model credentials only in your environment. This repository accepts DeepSeek/GLM model IDs; records never include keys. PDF/text uploads are processed in memory and are not saved by the application. Only selected, visible evidence is sent to a configured model provider. Do not upload confidential material without the required permission.

Hash-linked traces are locally inspectable and detect an altered entry against its existing chain; a party controlling a whole trace can recompute it. They are not independently certified timestamps. Exact citation matching is not a guarantee of semantic correctness.

For a credential accidentally disclosed in chat or elsewhere, revoke and replace it in the issuing service. Do not paste credentials into Issues or screenshots.
