# Gen V Backend Package (`gtech-gen-v`)

This directory contains the core Python package for the main Gen V project.

The code builds the **`gtech-gen-v`** distribution package (the name used by
`pip`), which provides the **`gen_v`** import package (the name used in Python
`import` statements).

## Purpose

This package provides reusable components to support the AI-powered video ad
generation workflow.

Refer to the main project [README](../README.md) for the overall project
description, goals, and setup instructions for the Colab notebook environment.

## Structure

This package currently uses a **flat layout**:

* Package source code resides directly within the `gen_v/` directory.
* Unit tests are located in the `tests/` directory.

## Installation (for Development)

To use this package locally (e.g. for testing, contributing, or importing into
the Colab notebook), you need to install the `gtech-gen-v` distribution package.
The recommended way for development is an editable installation:

```bash
pip install -e ".[dev]"
```

The `-e` flag means changes you make to the source code in the `gen_v/`
directory will be reflected immediately without needing to reinstall.

## Usage

Once the `gtech-gen-v` distribution package is installed, components can be
imported into Python scripts or notebooks using the `gen_v` import name:

```python
from gen_v.models import VideoInput

video_info = VideoInput(path='/path/to/my/video.mp4')
```

## Managing Dependencies

This project uses `pip-tools` to manage dependencies and ensure reproducible
builds. Dependencies are specified in `requirements.in`, and the actual
installable dependency list (with hashes for security) is generated in
`requirements.txt`.

### Adding or Updating Dependencies

1. Edit the appropriate `.in` file:
    * `requirements.in`: For core project dependencies.
    * `requirements_dev.in`: For development-specific dependencies (e.g testing
      tools).

    Add, remove, or update package versions in the chosen file. List only the
    top-level dependencies.

    ```
    # requirements.in (Example)
    pydantic==2.11.1

    # requirements_dev.in (Example)
    pytest==8.3.5
    ```
2.  Generate the corresponding `requirements.txt` file by running the following
    commands to update the `requirements.txt` and/or `requirements_dev.txt`
    file(s) with the correct versions and hashes:

    ```bash
    pip-compile --generate-hashes --no-annotate --output-file=requirements.txt requirements.in
    pip-compile --generate-hashes --no-annotate --allow-unsafe --output-file=requirements_dev.txt requirements_dev.in
    ```

## Code Quality and Formatting

This project uses several tools to ensure code quality and consistent
formatting.

First install the dev requirements:
```bash
pip install --require-hashes -r requirements_dev.txt
```
Then you can run:

- Pylint: For static code analysis and linting. Run `pylint --recursive=y .` to
  check your code. The Pylint configuration is in `.pylintrc`.
- Pyink: For code formatting run `pyink .`. The configuration is specified in
  `pyproject.toml`

## Testing

*   Tests are located in the `tests` directory.
*   Use `pytest` to run the tests:

    ```bash
    pytest
    ```

## Disclaimer

> **Note:** This solution uses AI to edit or generate assets for your ads. Whether your content requires labeling depends on the nature of your assets, where your ads serve, and specific legal obligations that apply to you. In some circumstances Google may automatically apply a label. Please consult with your legal team to determine if/when a label is required for your ads. You can add labels in Google’s Ads products using the [AI label setting](https://support.google.com/google-ads/answer/17140115).

