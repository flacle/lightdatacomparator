import unittest
import os
from ldc import (
    generate_checksums,
    save_manifest_encrypted,
    load_manifest_encrypted,
    compare_manifests,
)

class TestLDC(unittest.TestCase):
    """
    TestCase subclass that contains unit tests for the Light Data Comparator (LDC) module. 
    It tests functionalities such as generating checksums for files in directories, computing overall checksums, 
    saving and loading manifests with encryption, and comparing manifests to detect added, deleted, or modified files.

    Methods:
        setUp(self):
            Sets up the test environment by defining test directories and passwords used in the tests.

        test_generate_checksums_folder_a(self):
            Tests that the generate_checksums function correctly computes the checksum for files in 'test_folder_a'.

        test_generate_checksums_folder_b(self):
            Tests that the generate_checksums function correctly computes the checksum for files in 'test_folder_b'.

        test_generate_checksums_folder_c(self):
            Tests that the generate_checksums function correctly computes checksums for files in 'test_folder_c'.

        test_save_and_load_manifest(self):
            Tests the ability to save a manifest file with encryption and then load it correctly.

        test_compare_manifests_added_file(self):
            Tests that `compare_manifests` correctly identifies files that have been added between two manifests.

        test_compare_manifests_modified_file(self):
            Tests that `compare_manifests` correctly identifies files that have been modified between two manifests.

        test_compare_manifests_deleted_file(self):
            Tests that `compare_manifests` correctly identifies files that have been deleted between two manifests.
    """
    def setUp(self):
        """Sets up the test environment by defining test directories and passwords used in the tests."""
        self.test_dir = os.path.abspath('test_folders')
        self.folder_a = os.path.join(self.test_dir, 'test_folder_a')
        self.folder_b = os.path.join(self.test_dir, 'test_folder_b')
        self.folder_c = os.path.join(self.test_dir, 'test_folder_c')
        self.password = 'testpassword'

    def test_generate_checksums_folder_a(self):
        """Tests that the generate_checksums function correctly computes the checksum for files in 'test_folder_a'."""
        checksums = generate_checksums(self.folder_a)
        self.assertEqual(len(checksums), 1)
        self.assertEqual(checksums[0][0], 'a.txt')

    def test_generate_checksums_folder_b(self):
        """Tests that the generate_checksums function correctly computes the checksum for files in 'test_folder_b'."""
        checksums = generate_checksums(self.folder_b)
        self.assertEqual(len(checksums), 1)
        self.assertEqual(checksums[0][0], 'a.txt')

    def test_generate_checksums_folder_c(self):
        """Tests that the generate_checksums function correctly computes checksums for files in 'test_folder_c'."""
        checksums = generate_checksums(self.folder_c)
        self.assertEqual(len(checksums), 2)
        paths = set(path for path, _ in checksums)
        self.assertSetEqual(paths, {'a.txt', 'b.txt'})

    def test_save_and_load_manifest(self):
        """Tests the ability to save a manifest file with encryption and then load it correctly."""
        checksums = generate_checksums(self.folder_a)
        manifest_filename = save_manifest_encrypted(checksums, self.password)
        self.assertTrue(os.path.exists(manifest_filename))
        loaded_checksums = load_manifest_encrypted(manifest_filename, self.password)
        self.assertEqual(checksums, loaded_checksums)
        os.remove(manifest_filename)

    def test_compare_manifests_added_file(self):
        """Tests that `compare_manifests` correctly identifies files that have been added between two manifests."""
        checksums_a = generate_checksums(self.folder_a)
        manifest_a_filename = save_manifest_encrypted(checksums_a, self.password)
        checksums_c = generate_checksums(self.folder_c)
        manifest_c_filename = save_manifest_encrypted(checksums_c, self.password)
        manifest_a = load_manifest_encrypted(manifest_a_filename, self.password)
        manifest_c = load_manifest_encrypted(manifest_c_filename, self.password)
        added, _, _ = compare_manifests(manifest_a, manifest_c)
        self.assertIn('b.txt', added)
        os.remove(manifest_a_filename)
        os.remove(manifest_c_filename)

    def test_compare_manifests_modified_file(self):
        """Tests that `compare_manifests` correctly identifies files that have been modified between two manifests."""
        checksums_a = generate_checksums(self.folder_a)
        manifest_a_filename = save_manifest_encrypted(checksums_a, self.password)
        checksums_b = generate_checksums(self.folder_b)
        manifest_b_filename = save_manifest_encrypted(checksums_b, self.password)
        manifest_a = load_manifest_encrypted(manifest_a_filename, self.password)
        manifest_b = load_manifest_encrypted(manifest_b_filename, self.password)
        _, _, modified = compare_manifests(manifest_a, manifest_b)
        self.assertIn('a.txt', modified)
        os.remove(manifest_a_filename)
        os.remove(manifest_b_filename)

    def test_compare_manifests_deleted_file(self):
        """Tests that `compare_manifests` correctly identifies files that have been deleted between two manifests."""
        checksums_c = generate_checksums(self.folder_c)
        manifest_c_filename = save_manifest_encrypted(checksums_c, self.password)
        checksums_a = generate_checksums(self.folder_a)
        manifest_a_filename = save_manifest_encrypted(checksums_a, self.password)
        manifest_c = load_manifest_encrypted(manifest_c_filename, self.password)
        manifest_a = load_manifest_encrypted(manifest_a_filename, self.password)
        _, deleted, _ = compare_manifests(manifest_c, manifest_a)
        self.assertIn('b.txt', deleted)
        os.remove(manifest_c_filename)
        os.remove(manifest_a_filename)

if __name__ == '__main__':
    unittest.main()