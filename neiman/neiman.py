import numpy as np
import struct
import sys
from vars import *


regs_dict = {
	1: REG_1,
	2: REG_2,
	3: REG_3,
	4: REG_4,
}

memory = np.zeros(MEMORY_SIZE, dtype=int)

def find_var_addr(var_id):
	#print([i for i in memory])
	#print('to_find', var_id + memory[RETURN_POINER])
	ind = stack_pointer
	while memory[ind] != var_id + memory[RETURN_POINER] and ind < MEMORY_SIZE:
		ind += 2
	'''
	if ind < MEMORY_SIZE:
		print('FOUND', ind)
	else:
		print('NOT FOUND')
	'''
	return ind

if __name__ == '__main__':

	data = open('binary_code', mode='rb').read()

	for i in range(0, len(data), 4):
		memory[i // 4] = int.from_bytes(data[i:i + 4], 'little', signed=True)

	ind = len(memory[:-6]) - 1
	while memory[ind] == 0:
		ind -= 1
	memory[ind+1] = 999999
	stack_pointer = ind + 2
	#print('stack_pointer', stack_pointer)
	memory[SP] = stack_pointer

	memory[RETURN_POINER] = RETURN_POINER
	#print([i for i in memory])

	while (True):
		ip = memory[IP]
		#print([i for i in memory])
		if (memory[ip] == SUM):
			#print('SUM')
			a = memory[ip+1]
			b = memory[ip+2]
			to = memory[ip+3]
			memory[regs_dict[to]] = memory[find_var_addr(a)+1] + memory[find_var_addr(b)+1]
			memory[IP] += 4

		elif memory[ip] == VAR:
			#print('VAR')
			var_id =  memory[ip+1]
			value = memory[ip+2]
			memory[memory[SP]] = var_id + memory[RETURN_POINER] # чтобы одинаковые переменные отличались в разных вызовах рекурсии
			memory[memory[SP]+1] = value
			#print(memory[SP])
			memory[SP] += 2
			memory[IP] += 3

		elif (memory[ip] == DEC):
			#print('DEC')
			a = memory[ip+1]
			b = memory[ip+2]
			to = memory[ip+3]
			memory[find_var_addr(to)+1] = memory[regs_dict[a]] - memory[regs_dict[b]]
			memory[IP] += 4

		elif (memory[ip] == PRINT_REG):
			#print('PRINT_REG')
			reg = memory[ip+1]
			print(memory[regs_dict[reg]])
			memory[IP] += 2

		elif (memory[ip] == EQUAL):
			#print('EQUAL')
			a = memory[ip+1]
			b = memory[ip+2]
			to = memory[ip+3]
			memory[regs_dict[to]] = memory[regs_dict[a]] == memory[regs_dict[b]]
			memory[IP] += 4

		elif (memory[ip] == MOVE_REG_TO_REG):
			#print('MOVE_REG_TO_REG')
			what = memory[ip+1]
			to = memory[ip+2]
			memory[regs_dict[to]] = memory[regs_dict[what]]
			memory[IP] += 3

		elif memory[ip] == MOVE_VAR_TO_VAR:
			#print('MOVE_VAR_TO_VAR')
			what = memory[ip+1]
			to = memory[ip+2]
			memory[find_var_addr(to)+1] = memory[find_var_addr(what)+1]
			memory[IP] += 3

		elif memory[ip] == MOVE_REG_TO_VAR:
			#print('MOVE_REG_TO_VAR')
			what = memory[ip+1]
			to = memory[ip+2]
			memory[find_var_addr(to)+1] = memory[regs_dict[what]]
			memory[IP] += 3

		elif memory[ip] == MOVE_VAR_TO_REG:
			#print('MOVE_VAR_TO_REG')
			what = memory[ip+1]
			to = memory[ip+2]
			memory[regs_dict[to]] = memory[find_var_addr(what)+1]
			memory[IP] += 3

		elif (memory[ip] == MOVE_INT):
			#print('MOVE_INT')
			what = memory[ip+1]
			to = memory[ip+2]
			memory[regs_dict[to]] = memory[what]
			memory[IP] += 3

		elif (memory[ip] == PRINT):
			#print('PRINT')
			length = memory[ip+1]
			s = struct.pack('<' + 'i' * length, *memory[ip+2:ip+2+length])
			print(s.decode('utf-8'))
			memory[IP] += 2+length

		elif (memory[ip] == READ):
			#print('READ')
			reg_to_write = memory[ip+1]
			n = int(sys.stdin.readline())
			memory[regs_dict[reg_to_write]] = n
			memory[IP] += 2

		elif (memory[ip] == CALL):
			#print('CALL')
			func_addr = memory[ip+1]
			memory[RETURN_POINER] -= 1
			memory[memory[RETURN_POINER]] = ip+2
			memory[IP] = func_addr

		elif (memory[ip] == EXIT):
			#print('EXIT')
			break;

		elif (memory[ip] == RETURN):
			#print('RETURN')
			memory[IP] = memory[memory[RETURN_POINER]]
			memory[RETURN_POINER] += 1

		elif (memory[ip] == IF_RETURN):
			#print('IF_RETURN')
			reg = memory[ip+1]
			return_value = memory[ip+2]
			if memory[regs_dict[reg]] == 1:
				#print("if_true")
				memory[regs_dict[3]] = return_value
				memory[IP] = memory[memory[RETURN_POINER]]
				memory[RETURN_POINER] += 1
			else:
				#print("if_false")
				memory[IP] += 3

		else:
			raise NotImplementedError(memory[ip])	



