# Light Data Checker

This lightweight Python script helps you compare the contents of one root folder with those of another that is not part of an information tracker such as Git.

## Problem Use Case

Sometimes, you or your team members change a file in a folder. Suppose this folder contains raw data that feeds into a dataset or any other content. This folder is by design not versioned; it is not part of a repository. It can quickly happen that this change goes unnoticed. Suppose you have the same directory tree on another machine; how can you reduce the risk of a change going unnoticed?

## Solution

One approach is to generate checksums for files in a directory tree and save these in a manifest file, which this script does. You can then compare manifests to identify differences between directory states. This solution can be part of a data processing or training pipeline where you would apply the comparison to assert equality before loading the data for further processing.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/flacle/lightdatachecker.git
```

The goal is to keep this lightweight, so no dependencies are needed. The script uses Python's built-in libraries.

**NOTE: The script is written in Python 3.12.2. It may work with other versions, but it has not been tested.**

## Usage

Run with the following command:

```bash
python ldc.py <command> [options]
```

### Commands

- `directory`: Root directory to compute checksums for.
- `--password`: Password to encrypt the manifest file (Required).
- `--output`: Output file path for the manifest (use only when not comparing).
- `--compare`: Path to an existing manifest file to compare against.

#### Notes

- The password is for obfuscation purposes only. Do not use this for sensitive data.
- The manifest file is saved with a custom `.checker` extension.
- You can use the `--output` option to generate a manifest file on a shared network drive.
- This repository contains a unit test script with a sample directory to test the script.

### Example Usage

Generate a manifest file for a directory:

```bash
python ldc.py /path/to/directory --password your_password --output manifest.checker
```

Compare directory with existing manifest file:

```bash
python ldc.py /path/to/directory --password your_password --compare previous_manifest.checker
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.