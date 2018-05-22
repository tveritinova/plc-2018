import numpy as np
from vars import *
import struct
import functools

regs_dict = {}
regs_dict['r1'] = 1
regs_dict['r2'] = 2
regs_dict['r3'] = 3
regs_dict['r4'] = 4

if __name__ == '__main__':
	code = open('fib', mode='r')

	memory = np.zeros(MEMORY_SIZE)

	parts = code.readline()[:-1].split(' ')

	cur_addr = 0

	funcs_addr = {}

	var_id = 1
	vars_dict = {}

	while parts[0] != '':

		if parts[0] == 'def':
			name = parts[1]
			funcs_addr[name] = cur_addr

			if name == 'main':
				memory[IP] = cur_addr
			
			parts = code.readline()[:-1].split(' ')

			while parts[0] != 'enddef' and parts[0] != 'endde':

				if parts[0] == 'var':
					name = parts[1]
					value = parts[2]
					vars_dict[name] = var_id
					var_id += 1
					memory[cur_addr] = VAR
					memory[cur_addr+1] = vars_dict[name]
					memory[cur_addr+2] = value
					cur_addr += 3

				elif parts[0] == 'print':
					memory[cur_addr] = PRINT
					array = bytearray(functools.reduce(lambda x, y: x+' '+y, parts[1:]), 'utf8')
					memory[cur_addr+1] = len(array)
					for i in range(cur_addr+2,cur_addr+2+len(array)):
						memory[i] = array[i-cur_addr-2]
					cur_addr += 2 + len(array)

				elif parts[0] == 'print_reg':
					reg_to_print = regs_dict[parts[1]]
					memory[cur_addr] = PRINT_REG 
					memory[cur_addr+1] = reg_to_print
					cur_addr += 2

				elif parts[0] == 'read':
					reg_to_write = regs_dict[parts[1]]
					memory[cur_addr] = READ
					memory[cur_addr+1] = reg_to_write
					cur_addr += 2

				elif parts[0] == "move":
					what = parts[1]
					to = parts[2]

					flag_to_var = to in vars_dict
					flag_to_reg = to in regs_dict
					flag_what_var = what in vars_dict
					flag_what_reg = what in regs_dict

					if flag_to_reg and flag_what_reg:
						to = regs_dict[to]
						what = regs_dict[what]
						memory[cur_addr] = MOVE_REG_TO_REG 

					if flag_to_var and flag_what_reg:
						to = vars_dict[to]
						what = regs_dict[what]
						memory[cur_addr] = MOVE_REG_TO_VAR

					if flag_to_reg and flag_what_var:
						to = regs_dict[to]
						what = vars_dict[what]
						memory[cur_addr] = MOVE_VAR_TO_REG

					if flag_to_var and flag_what_var:
						to = vars_dict[to]
						what = vars_dict[what]
						memory[cur_addr] = MOVE_VAR_TO_VAR

					if not flag_what_reg and not flag_what_var:
						if flag_to_var:
							to = vars_dict[to]
						if flag_to_reg:
							to = regs_dict[to]
						memory[cur_addr] = MOVE_INT

					memory[cur_addr+1] = what
					memory[cur_addr+2] = to
					cur_addr += 3

				elif parts[0] == "sum":
					memory[cur_addr] = SUM
					a = vars_dict[parts[1]]
					b = vars_dict[parts[2]]
					to = regs_dict[parts[3]]
					memory[cur_addr+1] = a
					memory[cur_addr+2] = b
					memory[cur_addr+3] = to
					cur_addr += 4

				elif parts[0] == "dec":
					memory[cur_addr] = DEC
					a = regs_dict[parts[1]]
					b = regs_dict[parts[2]]
					to = vars_dict[parts[3]]
					memory[cur_addr+1] = a
					memory[cur_addr+2] = b
					memory[cur_addr+3] = to
					cur_addr += 4

				elif parts[0] == "eq":
					memory[cur_addr] = EQUAL
					a = regs_dict[parts[1]]
					b = regs_dict[parts[2]]
					to = regs_dict[parts[3]]
					memory[cur_addr+1] = a
					memory[cur_addr+2] = b
					memory[cur_addr+3] = to
					cur_addr += 4

				elif parts[0] == "call":
					func_name = parts[1]
					memory[cur_addr] = CALL
					memory[cur_addr+1] = funcs_addr[func_name]
					cur_addr += 2

				elif parts[0] == "return":
					memory[cur_addr] = RETURN
					cur_addr += 1

				elif parts[0] == "exit":
					memory[cur_addr] = EXIT
					cur_addr += 1

				elif parts[0] == "if_return":
					reg = regs_dict[parts[1]]
					return_value = parts[2]
					memory[cur_addr] = IF_RETURN
					memory[cur_addr+1] = reg
					memory[cur_addr+2] = return_value
					cur_addr += 3
					
				else:
					raise NotImplementedError(parts[0])					


				parts = code.readline()[:-1].split(' ')

		parts = code.readline()[:-1].split(' ')

	print [i for i in memory]
	open('binary_code', 'wb').write(struct.pack('<' + 'i' * len(memory), *memory)) 
