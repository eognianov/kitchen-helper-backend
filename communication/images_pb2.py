# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: images.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cimages.proto\x12\x06images\" \n\x0cImageRequest\x12\x10\n\x08image_id\x18\x01 \x01(\x03\"5\n\rImageResponse\x12\x16\n\timage_url\x18\x01 \x01(\tH\x00\x88\x01\x01\x42\x0c\n\n_image_url2F\n\x06Images\x12<\n\rget_image_url\x12\x14.images.ImageRequest\x1a\x15.images.ImageResponseb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'images_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_IMAGEREQUEST']._serialized_start = 24
    _globals['_IMAGEREQUEST']._serialized_end = 56
    _globals['_IMAGERESPONSE']._serialized_start = 58
    _globals['_IMAGERESPONSE']._serialized_end = 111
    _globals['_IMAGES']._serialized_start = 113
    _globals['_IMAGES']._serialized_end = 183
# @@protoc_insertion_point(module_scope)