#!/usr/bin/python

import base64
from proto.ved_pb2 import Ved

'''
	The type of link encoded in the ved message. If you find out, what other values mean,
	please either send me a pull request or comment in the article
	(http://gqs-decoder.blogspot.com/2013/08/google-referrer-query-strings-debunked-part-1.html)
'''
LINK_TYPES = {
	22   : 'web',
	429  : 'image',
	311  : 'video',
	1617 : 'advertisement'
}

def try_decode(s):
	''' try to base64 decode s. return None, if decoding fails '''
	try:
		return base64.b64decode(str(s)+'=====', '_-')
	except TypeError:
		return None

def decode_ved_plain(s):
	''' decode the plain text varian of the ved parameter. no error checking. '''

	key_mapping = {'i':'index_boost', 't':'type', 'r':'result_position', 's':'start'}

	kv_pairs = s.split(',')
	kv_pairs = map(lambda x: x.split(':'), kv_pairs)
	kv_pairs = map(lambda (k,v): (key_mapping[k], int(v)), kv_pairs)
	return dict(kv_pairs)

def decode_ved_protobuf(s):
	''' decode the protobuf variant of the ved parameter. '''

	decoded  = try_decode(s)
	if not decoded:
		return None
	ved = Ved()
	try:
		ved.ParseFromString(decoded)

		ret = {}
		for k,v in ved.ListFields():
			ret[k.name] = v
		return ret
	except DecodeError: 
		return None

def decode_ved(s):
	''' decode a ved '''
	if not s:
		return None
	if s[0] == '1': #TODO: decode plain text variant
		return decode_ved_plain(s[1:])
	elif s[0] == '0':
		return decode_ved_protobuf(s[1:])

def format_type(type):
	type_name = LINK_TYPES.get(type, 'unknown')
	return '%s (%s)' % (type_name, type)

def format_ved(ved):
	if 'type' in ved:
		ved['type'] = format_type(ved['type'])
	return ved

def main():
	import sys
	for line in sys.stdin:
		line = line.strip()
		if not line:
			continue
		print format_ved(decode_ved(line))

if __name__ == '__main__':
	main()
