#!/usr/bin/python3
from dataclasses import dataclass
import typing
import struct
import numpy as np

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

	def __init__(self):
		self.mtx = [1,0,0, 0,1,0, 0,0,1]
		self.pos = [0,0,0]

	def read(self, file):
		self.mtx = struct.unpack(">9f", file.read(9 * 4))
		self.pos = struct.unpack(">3f", file.read(3 * 4))

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

	def read(self, file):
		import sys
		self.x, self.y, self.z = struct.unpack(">3f", file.read(12))
		# note: assumes non-UI mesh!!!
		assert struct.unpack(">i", file.read(4)) != -1
		file.seek(-4, 1)
		self.u = float(numpy.frombuffer(file.read(4), numpy.float16, 1, 0))
		self.v = float(numpy.frombuffer(file.read(4), numpy.float16, 1, 0))
		# qtangent (stores both normals and tangents in 4 shorts, presumably using clown math)
		struct.unpack(">4h", file.read(8))
		# weights + bone indices
		self.weight_0, self.weight_1, self.weight_2, self.weight_3 = struct.unpack(">4B", file.read(4))
		bone_0, bone_1, bone_2, bone_3 = struct.unpack(">4H", file.read(8))

	def write(self, file):
		file.write(struct.pack(">3f", self.x, self.y, self.z))
		# note: assumes non-UI mesh!!!
		file.write(np.float16(self.u).tobytes())
		file.write(np.float16(self.v).tobytes())
		# qtangent (stores both normals and tangents in 4 shorts, presumably using clown math)
		file.write(struct.pack(">4h", 0,0,0,0))
		# weights + bone indices
		file.write(struct.pack(">4B", 255,255,255,255))
		file.write(struct.pack(">4H", 0, 1, 2, 3))


@dataclass
class Face:
	i0: int
	i1: int
	i2: int

	def read(self, file):
		self.i0, self.i1, self.i2 = struct.unpack(">3H", file.read(6))

@dataclass
class Bone:
	name: str
	xfm: Xfm

	def read(self, file):
		self.name = read_pascal_str(file)
		self.xfm.read(file)

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
		assert self.version == 38
		self.obj_ver = struct.unpack(">i", file.read(4))[0]
		self.milotype = read_pascal_str(file)
		self.has_typeprops = struct.unpack("?", file.read(1))[0]
		self.note = read_pascal_str(file)
		self.trans_ver = struct.unpack(">i", file.read(4))[0]
		self.local.read(file)
		self.world.read(file)
		self.constraint = struct.unpack(">i", file.read(4))[0]
		self.target = read_pascal_str(file)
		self.preserve_scale = struct.unpack("?", file.read(1))[0]
		self.parent = read_pascal_str(file)
		self.draw_ver = struct.unpack(">i", file.read(4))[0]
		self.showing = struct.unpack("?", file.read(1))[0]
		self.bound = Sphere(*struct.unpack(">4f", file.read(16)))
		self.z_order = struct.unpack(">f", file.read(4))[0]
		self.material = read_pascal_str(file)
		self.geom_owner = read_pascal_str(file)
		self.mutable = struct.unpack(">i", file.read(4))[0]
		self.volume = struct.unpack(">i", file.read(4))[0]
		self.is_bsp = struct.unpack("?", file.read(1))[0]
		self.vert_ct = struct.unpack(">i", file.read(4))[0]
		self.is_ng = struct.unpack("?", file.read(1))[0]
		self.vert_size = struct.unpack(">i", file.read(4))[0]
		self.something = struct.unpack(">i", file.read(4))[0]
		self.verts = [Vertex(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0) for _ in range(self.vert_ct)]
		[v.read(file) for v in self.verts]
		self.face_ct = struct.unpack(">i", file.read(4))[0]
		self.faces = [Face(0,0,0) for _ in range(self.face_ct)]
		[f.read(file) for f in self.faces]
		self.group_size_ct = struct.unpack(">i", file.read(4))[0]
		if (self.group_size_ct > 0):
			self.group_sizes = struct.unpack(f">{self.group_size_ct}B", file.read(self.group_size_ct))
		self.bone_ct = struct.unpack(">i", file.read(4))[0]
		self.bones = [Bone("", Xfm()) for _ in range(self.bone_ct)]
		[b.read(file) for b in self.bones]
		self.keep_data = struct.unpack("?", file.read(1))[0]
		self.does_ao = struct.unpack("?", file.read(1))[0]

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
	import tempfile as tf

	milo = open("test.milo_ps3", "rb")
	milo_data = milo.read()
	milo_entries = milo_data.split(b"\xAD\xDE\xAD\xDE")
	mesh_data = milo_entries[3]
	print(mesh_data)
	mesh_obj = Mesh(0,0,"",False,"",0,Xfm(), Xfm(), 0, "", False, "", 0, True, Sphere(0,0,0,0), 0.0, "", "", 0, 0, False, 0, True, 0, 0, [], 0, [], 0, [], 0, [], True, True)
	_tmpf = tf.TemporaryFile("r+b")
	_tmpf.write(mesh_data)
	_tmpf.seek(0)
	mesh_obj.read(_tmpf)
	left = _tmpf.read()
	print(len(left))
