import os
import sys
import hashlib
import argparse
from pathlib import Path

# Define system files to ignore
IGNORED_FILES = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}

def compute_file_checksum(file_path):
    """Compute SHA-256 checksum of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read and update hash in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def generate_checksums(root_dir):
    """Generate checksums for all files in the directory tree."""
    checksums = []
    root_path = Path(root_dir).resolve()
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(root_path)
            if relative_path.name in IGNORED_FILES:
                continue
            file_checksum = compute_file_checksum(file_path)
            # Normalize the relative path to use forward slashes
            normalized_path = relative_path.as_posix()
            checksums.append((normalized_path, file_checksum))
    # Sort the list to ensure consistent order
    checksums.sort()
    return checksums

def simple_encrypt_decrypt(content, password):
    """Encrypt or decrypt content using a simple XOR cipher."""
    key = hashlib.sha256(password.encode('utf-8')).digest()
    encrypted = bytearray()
    for i in range(len(content)):
        encrypted.append(content[i] ^ key[i % len(key)])
    return bytes(encrypted)

def save_manifest_encrypted(checksums, password, output_path=None):
    """Save the per-file checksums to an encrypted manifest file."""
    manifest_content = '\n'.join(f'{checksum}  {path}' for path, checksum in checksums)
    # Add a known header to the manifest content
    manifest_content = 'MANIFEST_HEADER' + manifest_content
    manifest_bytes = manifest_content.encode('utf-8')
    encrypted_manifest = simple_encrypt_decrypt(manifest_bytes, password)
    # Compute the hash of the manifest content for the filename
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest_filename = f'{manifest_hash}.comparator'
    #  if output_path is not provided
    if output_path:
        # `output_path` is always a directory
        manifest_filename = os.path.join(output_path, manifest_filename)
    with open(manifest_filename, 'wb') as f:
        f.write(encrypted_manifest)
    return manifest_filename

def load_manifest_encrypted(manifest_file, password):
    """Load and decrypt checksums from an encrypted manifest file."""
    with open(manifest_file, 'rb') as f:
        encrypted_content = f.read()
    decrypted_content = simple_encrypt_decrypt(encrypted_content, password)
    try:
        manifest_text = decrypted_content.decode('utf-8')
        # Verify the header
        if not manifest_text.startswith('MANIFEST_HEADER'):
            raise ValueError('Incorrect password or corrupted manifest file.')
        # Remove the header before processing
        manifest_text = manifest_text[len('MANIFEST_HEADER'):]
    except (UnicodeDecodeError, ValueError) as e:
        raise ValueError('Incorrect password or corrupted manifest file.') from e
    checksums = []
    for line in manifest_text.strip().split('\n'):
        checksum, path = line.strip().split('  ', 1)
        checksums.append((path, checksum))
    return checksums

def compare_manifests(manifest1, manifest2):
    """Compare two manifests and categorize differences."""
    checksums1 = dict(manifest1)
    checksums2 = dict(manifest2)
    all_keys = set(checksums1.keys()) | set(checksums2.keys())
    added = []
    deleted = []
    modified = []
    for key in all_keys:
        checksum1 = checksums1.get(key)
        checksum2 = checksums2.get(key)
        if checksum1 != checksum2:
            if checksum1 is None:
                added.append(key)
            elif checksum2 is None:
                deleted.append(key)
            else:
                modified.append(key)
    return added, deleted, modified

def main():
    """
    Compute directory checksums, save the encrypted manifest, and optionally compare with another manifest.

    This function parses command-line arguments to compute checksums of all files in a specified directory,
    encrypts and saves the manifest using the provided password, and optionally compares the new manifest
    with an existing one to report any differences.

    Command-line Arguments:
        directory (str): Root directory to compute checksums for.
        --password (str): Password for encrypting the manifest.
        --output (str, optional): Path or filename to save the manifest.
        --compare (str, optional): Path to an existing manifest file to compare against.
    """
    parser = argparse.ArgumentParser(description='Compute directory checksum.')
    parser.add_argument('directory', help='Root directory to compute checksum for.')
    parser.add_argument('--password', required=True, help='Password for encrypting the manifest.')
    parser.add_argument('--output', help='Specify the output file path for the manifest (only when not comparing).')
    parser.add_argument('--compare', help='Compare directory with an existing manifest file.')
    args = parser.parse_args()

    # Validate that --output is only used when --compare is not specified
    if args.compare and args.output:
        parser.error("The '--output' argument cannot be used together with '--compare'.")

    try:
        # Generate checksums of the current directory
        checksums = generate_checksums(args.directory)
        # Save the manifest if not comparing
        if not args.compare:
            manifest_filename = save_manifest_encrypted(checksums, args.password, args.output)
            print(f'Manifest saved to: {manifest_filename}')
    except Exception as e:
        print(f'Error generating manifest: {e}')
        return

    if args.compare:
        if not os.path.isfile(args.compare):
            print(f'Error: The file {args.compare} does not exist.')
            return
        try:
            # Load checksums from the existing manifest file
            old_checksums = load_manifest_encrypted(args.compare, args.password)
        except ValueError as e:
            print(f'Error loading manifest: {e}')
            return
        # Compare the old checksums with the current checksums
        added, deleted, modified = compare_manifests(old_checksums, checksums)
        if added or deleted or modified:
            print('Differences found:')
            if added:
                print('Added files:')
                for file in added:
                    print(f' + {file}')
            if deleted:
                print('Deleted files:')
                for file in deleted:
                    print(f' - {file}')
            if modified:
                print('Modified files:')
                for file in modified:
                    print(f' * {file}')
        else:
            print('No differences found compared to the provided manifest.')

if __name__ == '__main__':
    main()