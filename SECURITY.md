# Security

Sentinela is a local research/demo application, not authentication or access control. Gesture sequences are observable and replayable. Do not connect successful detection directly to unlocking a device or granting account access.

Only load model checkpoints obtained from trusted sources. `.pt` checkpoints can contain Python pickle objects; checksum verification confirms expected bytes, not benign behavior. Do not disable framework safeguards to load a downloaded checkpoint. Runtime dependencies and model compatibility require ongoing review.

For a suspected vulnerability, use [GitHub private vulnerability reporting](https://github.com/marco-pcg/sentinela/security/advisories/new) if enabled. If that route is unavailable, contact the maintainer through a private channel listed on their GitHub profile; a public issue may request a private contact, but must not include exploit details, secrets or personal images. Private reporting availability and a dedicated contact are pending maintainer configuration.

There are no supported production releases or response-time guarantees yet. The default branch is the development target. CI audits dependency locks; it does not certify that a checkpoint is safe or that a deployment meets a security standard.
