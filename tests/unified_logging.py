# -*- coding: utf-8 -*-
"""Tests for Apple Unified Logging and Activity Tracing files."""

import io
import os
import unittest
import uuid

import lz4.block

from dtformats import unified_logging

from tests import test_lib


class DSCFileTest(test_lib.BaseTestCase):
  """Shared-Cache Strings (dsc) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertEqual(file_header.signature, b'hcsd')
    self.assertEqual(file_header.major_format_version, 2)
    self.assertEqual(file_header.minor_format_version, 0)
    self.assertEqual(file_header.number_of_ranges, 263)
    self.assertEqual(file_header.number_of_uuids, 200)

  def testReadRangeDescriptors(self):
    """Test the _ReadRangeDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 1, 252))

    self.assertEqual(len(ranges), 252)
    self.assertEqual(ranges[64].range_offset, 1756712)
    self.assertEqual(ranges[64].range_size, 3834)

    # Testing version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 2, 263))

    self.assertEqual(len(ranges), 263)
    self.assertEqual(ranges[10].range_offset, 64272)
    self.assertEqual(ranges[10].range_size, 39755)

  def testReadUUIDPath(self):
    """Tests the _ReadUUIDPath function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuid_path = test_file._ReadUUIDPath(file_object, 3202606)

    expected_uuid_path = (
        '/System/Library/Extensions/AppleBCMWLANFirmware_Hashstore.kext/'
        'AppleBCMWLANFirmware_Hashstore')
    self.assertEqual(uuid_path, expected_uuid_path)

  def testReadUUIDDescriptors(self):
    """Test the _ReadUUIDDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 4048, 1, 196))

    self.assertEqual(len(uuids), 196)
    self.assertEqual(uuids[42].text_offset, 9191424)
    self.assertEqual(uuids[42].text_size, 223732)
    expected_path = '/System/Library/Extensions/AppleH8ADBE0.kext/AppleH8ADBE0'
    self.assertEqual(uuids[42].path, expected_path)

    # Testing Version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 6328, 2, 200))

    self.assertEqual(len(uuids), 200)
    self.assertEqual(uuids[197].text_offset, 26816512)
    self.assertEqual(uuids[197].text_size, 43736)
    expected_path = (
        '/System/Library/Extensions/AppleD2207PMU.kext/AppleD2207PMU')
    self.assertEqual(uuids[197].path, expected_path)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    # TODO: test of 8E21CAB1DCF936B49F85CF860E6F34EC currently failing.
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
        # 'unified_logging', 'uuidtext', 'dsc',
        # '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class TimesyncDatabaseFileTest(test_lib.BaseTestCase):
  """Tests for the timesync database file."""

  # pylint: disable=protected-access

  def testReadFileRecord(self):
    """Tests the _ReadRecord method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      # Boot record
      record, _ = test_file._ReadRecord(file_object, 0)

      self.assertEqual(record.signature, b'\xb0\xbb')
      self.assertEqual(record.record_size, 48)
      self.assertEqual(record.timebase_numerator, 125)
      self.assertEqual(record.timebase_denominator, 3)
      self.assertEqual(record.timestamp, 1541730321839294000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

      # sync record
      record, _ = test_file._ReadRecord(file_object, 48)

      self.assertEqual(record.signature, b'Ts')
      self.assertEqual(record.record_size, 32)
      self.assertEqual(record.kernel_time, 494027973)
      self.assertEqual(record.timestamp, 1541730337313716000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

  def testReadFileObject(self):
    """Tests the ReadFileObject method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class TraceV3FileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (tracev3) file tests."""

  # pylint: disable=protected-access

  _FIREHOST_CHUNK_DATA = bytes(bytearray([
      0x92, 0x16, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd0, 0x3b, 0x15, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x18, 0x01, 0x00, 0x10, 0x00, 0x00, 0x01, 0x02,
      0x30, 0xb3, 0x7d, 0x7a, 0x48, 0x5b, 0x00, 0x00, 0x04, 0x00, 0x05, 0x06,
      0xcd, 0x83, 0x7c, 0x08, 0x0f, 0xe8, 0xae, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0xa0, 0x00, 0x20, 0x3b, 0xea, 0x00,
      0x00, 0x00, 0x00, 0x80, 0x64, 0xca, 0x6c, 0x08, 0x61, 0x00, 0x15, 0x22,
      0x02, 0x42, 0x04, 0x00, 0x00, 0x2c, 0x00, 0x22, 0x04, 0x2c, 0x00, 0x57,
      0x00, 0x73, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x67, 0x72, 0x6f, 0x75, 0x70,
      0x2e, 0x63, 0x6f, 0x6d, 0x2e, 0x61, 0x70, 0x70, 0x6c, 0x65, 0x2e, 0x63,
      0x6f, 0x6e, 0x66, 0x69, 0x67, 0x75, 0x72, 0x61, 0x74, 0x69, 0x6f, 0x6e,
      0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73, 0x00, 0x2f, 0x70, 0x72,
      0x69, 0x76, 0x61, 0x74, 0x65, 0x2f, 0x76, 0x61, 0x72, 0x2f, 0x63, 0x6f,
      0x6e, 0x74, 0x61, 0x69, 0x6e, 0x65, 0x72, 0x73, 0x2f, 0x53, 0x68, 0x61,
      0x72, 0x65, 0x64, 0x2f, 0x53, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x47, 0x72,
      0x6f, 0x75, 0x70, 0x2f, 0x73, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x67, 0x72,
      0x6f, 0x75, 0x70, 0x2e, 0x63, 0x6f, 0x6d, 0x2e, 0x61, 0x70, 0x70, 0x6c,
      0x65, 0x2e, 0x63, 0x6f, 0x6e, 0x66, 0x69, 0x67, 0x75, 0x72, 0x61, 0x74,
      0x69, 0x6f, 0x6e, 0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73, 0x00,
      0x04, 0x00, 0x04, 0x06, 0xb8, 0x4b, 0xa8, 0x01, 0x79, 0xe8, 0xae, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x6d, 0x72, 0xc4, 0x2c, 0x10, 0x00, 0x09, 0x00,
      0x94, 0x5a, 0xa2, 0x01, 0x7f, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x04, 0x06, 0xb8, 0x4b, 0xa8, 0x01,
      0x79, 0xe8, 0xae, 0x00, 0x00, 0x00, 0x00, 0x00, 0xcb, 0xbc, 0xc4, 0x2c,
      0x10, 0x00, 0x09, 0x00, 0x94, 0x5a, 0xa2, 0x01, 0x7f, 0x00, 0x03, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  _HEADER_CHUNK_DATA = bytes(bytearray([
      0x7d, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0xc2, 0x55, 0xe0, 0xb5,
      0x32, 0x3f, 0x00, 0x00, 0xb6, 0xcc, 0x56, 0x62, 0x00, 0x00, 0x00, 0x00,
      0x9a, 0x34, 0x05, 0x00, 0x2c, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
      0x01, 0x00, 0x00, 0x00, 0x00, 0x61, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00,
      0xc9, 0x23, 0xa5, 0x1e, 0x8c, 0x5b, 0x00, 0x00, 0x01, 0x61, 0x00, 0x00,
      0x38, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00,
      0x31, 0x39, 0x44, 0x35, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x4a, 0x39, 0x36, 0x41, 0x50, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x02, 0x61, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00, 0xa6, 0xeb, 0xc8, 0xe3,
      0x0a, 0x1c, 0x40, 0xe8, 0x93, 0xb9, 0xda, 0x3a, 0x7f, 0x67, 0x1d, 0x19,
      0x1e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x61, 0x00, 0x00,
      0x30, 0x00, 0x00, 0x00, 0x2f, 0x76, 0x61, 0x72, 0x2f, 0x64, 0x62, 0x2f,
      0x74, 0x69, 0x6d, 0x65, 0x7a, 0x6f, 0x6e, 0x65, 0x2f, 0x7a, 0x6f, 0x6e,
      0x65, 0x69, 0x6e, 0x66, 0x6f, 0x2f, 0x41, 0x6d, 0x65, 0x72, 0x69, 0x63,
      0x61, 0x2f, 0x54, 0x6f, 0x72, 0x6f, 0x6e, 0x74, 0x6f, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  _SIMPLEDUMP_CHUNK_DATA = bytes(bytearray([
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x4f, 0x95, 0xd2, 0x21, 0x00, 0x00, 0x00, 0x00,
      0x5f, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x44, 0x85, 0x03, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x1d, 0x62, 0x53, 0x53, 0xa9, 0xfa, 0x3e, 0xc9,
      0x94, 0xc0, 0xb2, 0x95, 0x23, 0x15, 0xb2, 0xd2, 0xbe, 0x7f, 0xe6, 0xad,
      0x45, 0x60, 0x3a, 0xe2, 0x88, 0x3e, 0x43, 0x2f, 0x78, 0xb4, 0x50, 0x62,
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2a, 0x00, 0x00, 0x00,
      0x53, 0x6b, 0x69, 0x70, 0x70, 0x69, 0x6e, 0x67, 0x20, 0x62, 0x6f, 0x6f,
      0x74, 0x2d, 0x74, 0x61, 0x73, 0x6b, 0x3a, 0x20, 0x72, 0x65, 0x73, 0x74,
      0x6f, 0x72, 0x65, 0x2d, 0x64, 0x61, 0x74, 0x61, 0x70, 0x61, 0x72, 0x74,
      0x69, 0x74, 0x69, 0x6f, 0x6e, 0x00 ]))

  _STATEDUMP_CHUNK_DATA = bytes(bytearray([
      0x91, 0x75, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0xca, 0x5b, 0x0d, 0x00,
      0x0e, 0x00, 0x00, 0x00, 0x83, 0xa3, 0x1d, 0x3a, 0x8d, 0x5b, 0x00, 0x00,
      0x29, 0xd2, 0xea, 0x00, 0x00, 0x00, 0x00, 0x80, 0x08, 0x1b, 0x5e, 0x9e,
      0x59, 0xea, 0x39, 0xcd, 0x83, 0xc9, 0xee, 0xdb, 0x68, 0xa8, 0x40, 0x76,
      0x01, 0x00, 0x00, 0x00, 0x2a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x53, 0x70, 0x72, 0x69, 0x6e, 0x67, 0x42, 0x6f,
      0x61, 0x72, 0x64, 0x20, 0x2d, 0x20, 0x43, 0x6f, 0x6d, 0x62, 0x69, 0x6e,
      0x65, 0x64, 0x20, 0x4c, 0x69, 0x73, 0x74, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x62, 0x70, 0x6c, 0x69,
      0x73, 0x74, 0x30, 0x30, 0x50, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x09]))

  # TODO: add tests for _FormatArrayOfStrings
  # TODO: add tests for _FormatArrayOfUUIDS
  # TODO: add tests for _FormatStreamAsSignature

  def testReadChunkHeader(self):
    """Tests the _ReadChunkHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadChunkHeader(file_object, 0)

  # TODO: add tests for _ReadCatalog
  # TODO: add tests for _ReadChunkSet

  def testReadFirehoseChunkData(self):
    """Tests the _ReadFirehoseChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    firehose_data = test_file._ReadFirehoseChunkData(
        self._FIREHOST_CHUNK_DATA, len(self._FIREHOST_CHUNK_DATA), 0)

    self.assertEqual(firehose_data.process_identifier1, 464530)
    self.assertEqual(firehose_data.process_identifier2, 1391568)
    self.assertEqual(firehose_data.public_data_size, 280)
    self.assertEqual(firehose_data.private_data_virtual_offset, 0x1000)
    self.assertEqual(firehose_data.base_continuous_time, 100366850831152)
    self.assertEqual(len(firehose_data.firehose_tracepoints), 3)

    firehose_tracepoint = firehose_data.firehose_tracepoints[0]
    self.assertEqual(firehose_tracepoint.continuous_time, 68719476736)
    self.assertEqual(firehose_tracepoint.data_size, 160)
    self.assertEqual(firehose_tracepoint.format_string_location, 142377933)
    self.assertEqual(firehose_tracepoint.thread_identifier, 11462671)

  def testReadHeaderChunk(self):
    """Tests the _ReadHeaderChunk function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    with io.BytesIO(self._HEADER_CHUNK_DATA) as file_object:
      header_chunk = test_file._ReadHeaderChunk(file_object, 0)

    self.assertEqual(header_chunk.timebase_numerator, 125)
    self.assertEqual(header_chunk.timebase_denominator, 3)
    self.assertEqual(header_chunk.time_zone_offset, 300)

    self.assertEqual(header_chunk.continuous.sub_chunk_tag, 0x6100)

    self.assertEqual(header_chunk.system_information.sub_chunk_tag, 0x6101)
    self.assertEqual(header_chunk.system_information.build_version, '19D52')
    self.assertEqual(header_chunk.system_information.hardware_model, 'J96AP')

    self.assertEqual(header_chunk.generation.sub_chunk_tag, 0x6102)
    self.assertEqual(header_chunk.generation.boot_identifier, uuid.UUID(
        'a6ebc8e3-0a1c-40e8-93b9-da3a7f671d19'))

    self.assertEqual(header_chunk.time_zone.sub_chunk_tag, 0x6103)
    self.assertEqual(header_chunk.time_zone.path, (
        '/var/db/timezone/zoneinfo/America/Toronto'))

  def testReadOversizeChunkData(self):
    """Tests the _ReadOversizeChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    # The 8th chunkset chunk of the first set
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(0x1cc48, os.SEEK_SET)
      chunk_data = file_object.read(16519)

    uncompressed_data = lz4.block.decompress(
        chunk_data[12:12 + 16503], uncompressed_size=64624)

    # data block #17
    data_offset = 0xfc8
    data_type_map = test_file._GetDataTypeMap('tracev3_chunk_header')
    chunkset_chunk_header = test_file._ReadStructureFromByteStream(
        uncompressed_data[data_offset:], data_offset, data_type_map,
        'chunk header')

    self.assertEqual(chunkset_chunk_header.chunk_tag, 0x6002)
    self.assertEqual(chunkset_chunk_header.chunk_data_size, 2078)

    data_offset += 16
    data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size

    oversize_chunk = test_file._ReadOversizeChunkData(
        uncompressed_data[data_offset:data_end_offset],
        chunkset_chunk_header.chunk_data_size, data_offset)

    self.assertEqual(oversize_chunk.process_identifier1, 449241)
    self.assertEqual(oversize_chunk.process_identifier2, 1345727)
    self.assertEqual(oversize_chunk.ttl, 30)
    self.assertEqual(oversize_chunk.unknown1, 0)
    self.assertEqual(oversize_chunk.unknown2, 0)
    self.assertEqual(oversize_chunk.continuous_time, 100657868900985)
    self.assertEqual(oversize_chunk.data_reference_index, 82)
    self.assertEqual(oversize_chunk.public_data_size, 2046)
    self.assertEqual(oversize_chunk.private_data_size, 0)

  def testReadSimpleDumpChunkData(self):
    """Tests the _ReadSimpleDumpChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    simpledump_chunk = test_file._ReadSimpleDumpChunkData(
        self._SIMPLEDUMP_CHUNK_DATA, len(self._SIMPLEDUMP_CHUNK_DATA), 0)

    self.assertEqual(simpledump_chunk.process_identifier1, 1)
    self.assertEqual(simpledump_chunk.process_identifier2, 7)
    self.assertEqual(simpledump_chunk.continuous_time, 567448911)
    self.assertEqual(simpledump_chunk.thread_identifier, 1887)
    self.assertEqual(simpledump_chunk.unknown1, 230724)
    self.assertEqual(simpledump_chunk.unknown2, 0x0000)
    self.assertEqual(simpledump_chunk.unknown3, 0x0000)
    self.assertEqual(simpledump_chunk.sender_identifier, uuid.UUID(
        '1d625353-a9fa-3ec9-94c0-b2952315b2d2'))
    self.assertEqual(simpledump_chunk.dsc_identifier, uuid.UUID(
        'be7fe6ad-4560-3ae2-883e-432f78b45062'))
    self.assertEqual(simpledump_chunk.unknown4, 1)
    self.assertEqual(simpledump_chunk.subsystem_string_size, 0)
    self.assertEqual(simpledump_chunk.message_string_size, 42)
    self.assertEqual(simpledump_chunk.subsystem_string, '')
    self.assertEqual(simpledump_chunk.message_string, (
        'Skipping boot-task: restore-datapartition'))

  def testReadStateDumpChunkData(self):
    """Tests the _ReadStateDumpChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    statedump_chunk = test_file._ReadStateDumpChunkData(
        self._STATEDUMP_CHUNK_DATA, len(self._STATEDUMP_CHUNK_DATA), 0)

    self.assertEqual(statedump_chunk.process_identifier1, 292241)
    self.assertEqual(statedump_chunk.process_identifier2, 875466)
    self.assertEqual(statedump_chunk.ttl, 14)
    self.assertEqual(statedump_chunk.unknown1, 0)
    self.assertEqual(statedump_chunk.unknown2, 0)
    self.assertEqual(statedump_chunk.continuous_time, 100662123537283)
    self.assertEqual(statedump_chunk.activity_identifier, 9223372036870165033)
    self.assertEqual(statedump_chunk.unknown3, uuid.UUID(
        '081b5e9e-59ea-39cd-83c9-eedb68a84076'))
    self.assertEqual(statedump_chunk.data_type, 1)
    self.assertEqual(statedump_chunk.data_size, 42)
    self.assertEqual(statedump_chunk.unknown4, b'\x00' * 64)
    self.assertEqual(statedump_chunk.unknown5, b'\x00' * 64)
    self.assertEqual(statedump_chunk.name, 'SpringBoard - Combined List')
    self.assertEqual(statedump_chunk.data, self._STATEDUMP_CHUNK_DATA[248:])

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class UUIDTextFileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (uuidtext) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


if __name__ == '__main__':
  unittest.main()
