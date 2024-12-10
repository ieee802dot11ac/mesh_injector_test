#!/usr/bin/python3
from dataclasses import dataclass
import typing
import struct

def read_pascal_str(file) -> str:
	leng = struct.unpack(">i", file.read(4))[0]
	ret = b""
	c = b' '
	for _ in range(leng):
		c = bytes(file.read(1))
		ret += c
	return str(ret)[2:-1]
	
@dataclass
class Sphere:
	x: float
	y: float
	z: float
	r: float

@dataclass
class Xfm:
	mtx: list[float]
	pos: list[float]

@dataclass
class Vertex:
	x: float
	y: float
	z: float
	nx: float
	ny: float
	nz: float
	u: float
	v: float
	tx: float
	ty: float
	tz: float
	weight_0: int
	weight_1: int
	weight_2: int
	weight_3: int
	bone_0: int
	bone_1: int
	bone_2: int
	bone_3: int

@dataclass
class Face:
	i0: int
	i1: int
	i2: int

@dataclass
class Bone:
	name: str
	xfm: Xfm

@dataclass
class Mesh:
	version: int
	obj_ver: int
	milotype: str
	has_typeprops: bool
	note: str
	trans_ver: int
	local: Xfm
	world: Xfm
	constraint: int
	target: str
	preserve_scale: bool
	parent: str
	draw_ver: int
	showing: bool
	bound: Sphere
	z_order: float
	material: str
	geom_owner: str
	mutable: int
	volume: int
	is_bsp: bool
	vert_ct: int
	is_ng: bool
	vert_size: int
	something: int
	verts: list[Vertex]
	face_ct: int
	faces: list[Face]
	group_size_ct: int
	group_sizes: list[int]
	bone_ct: int
	bones: list[Bone]
	keep_data: bool
	does_ao: bool

	def read(self, file):
		self.version = struct.unpack(">i", file.read(4))[0]
		self.obj_ver = struct.unpack(">i", file.read(4))[0]
		self.milotype = read_pascal_str(file)

def read_obj_to_vtx_face_tup(file) -> (list[Vertex], list[Face]):
	import re
	verts = list()
	faces = list()
	while True:
		x = file.readline()
		if x == "":
			break
		match x[0]:
			case 'v':
				if x[1] == ' ':
					positions = [float(idx) for idx in re.search(r"v ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)", x).groups()]
					verts.append(Vertex(positions[0], positions[1], positions[2], 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
			case 'f':
				indexes = [int(idx) for idx in re.search(r"f (\d)/.*/.* (\d)/.*/.* (\d)/.*/.*", x).groups()]
				faces.append(Face(*indexes))

	return (verts, faces)

if __name__ == "__main__":
	import sys

	milo = open("test.milo_ps3", "rb")
	milo_data = milo.read()
	milo_entries = milo_data.split(b"\xAD\xDE\xAD\xDE")
	mesh_data = milo_entries[1]
	[print(e) for e in milo_entries]
