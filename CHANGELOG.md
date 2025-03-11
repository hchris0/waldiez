# Changelog

## v0.2.2 -

- You can find the changes for each release in the integrated [CHANGELOG.md](https://github.com/waldiez/waldiez/blob/main/CHANGELOG.md) file.

## v0.2.1

- introduce waldiez_studio
- python dependency updates, including ag2 v0.6.0
- add waldiez extras: 'studio' and 'jupyter'
- Dev dependencies updates

## v0.2.0

- python dependency updates, including ag2 v0.6.0
- introduce waldiez_studio
- add waldiez studio and jupyter as waldiez extras
- Dev dependencies updates

## v0.1.20

- Fix models not using a default base_url if not provided
- Updated runner: try handling UnicodeDecodeError
- Ignore 'flaml.automl is not available' warning

## v0.1.19

- Updated runner: Make the call to install requirements public

## v0.1.18

- Removed custom IOStream
- Handle refreshing the environment after pip install
- Dev dependencies updates

## v0.1.17

- Updated ag2 to 0.5.3
- Fixed an issue using uuid instead of str for the flow id
- Updated runtime logging to start earlier

## v0.1.16

- Updated conflict checker to provide more detailed instructions on how to resolve conflicts

## v0.1.15

- Updated requirements. Force pydantic to >=2.0

## v0.1.14

- Updated cli to allow/ignore extra arguments
- Fixed typo in pydantic model
- Updated ag2 to 0.5.0
- Other dependency updates

## v0.1.13

- Fix cli start script in pyproject.toml

## v0.1.12

- Updated cli usage (use typer)
- Added a `check` command option to validate a flow
- Fixed an issue with `pip install {requirements}` giving `externally-managed-environment` error

## v0.1.11

- Added a conflict check for ag2 and autogen-agentchat
- Updated exporting skills: create a new file the the skill secrets
- Updated ag2 to 0.4.1
- Other dependency updates

## v0.1.10

- Fixed an issue with using a chromadb client without telemetry

## v0.1.9

- Fix quotes in paths
- Disable chromadb telemetry
- Dependency updates

## v0.1.8

- Change autogen-agentchat to ag2
- Requirement updates
- Minor doc changes

- ## v0.1.7

- Move `WaldiezIOStream` to `waldiez.io` module
- Move autogen imports to local imports
- Also Provide a container (docker/podman) image for running/exporting Waldiez flows

## v0.1.6

- Fix SyntaxError with quoted strings
- Update twisted to 24.10.0

## v0.1.5

- Fix Quoting issue in chat messages

## v0.1.4

- Fix #40 - AttributeError: 'NoneType' object has no attribute 'endswith' with keyword termination.

## v0.1.3

- Exporting: Use a separate file for the model API keys

## v0.1.2

- RAG: handle windows paths
- Remove max_tokens from agent data

## v0.1.1

- RAG: use string literals for paths, to avoid issues with backslashes in Windows

## v0.1.0

- Initial release
