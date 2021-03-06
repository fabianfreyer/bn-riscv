# Copyright 2020 Katharina Utz <katharina.utz@stud.uni-due.de>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from binaryninja import (Architecture, BranchType, Endianness, InstructionInfo,
                         RegisterInfo, log_info)

from .instruction import RVDisassembler, gen_token
from .lifter import Lifter

branch_ins = set([
    'beq', 'bne', 'beqz', 'bnez', 'bge', 'bgeu', 'blt', 'bltu', 'blez', 'bgez',
    'bltz', 'bgtz'
])

direct_call_ins = set(['jal', 'j'])
indirect_call_ins = set(['jalr', 'jr'])


class RISCV(Architecture):
    name = "riscv"

    address_size = 4
    default_int_size = 4
    max_instr_length = 4

    endianness = Endianness.LittleEndian

    disassembler = RVDisassembler(address_size)
    lifter = Lifter(address_size)

    # we are using the ABI names here, as those are also the register names
    # returned by capstone.
    regs = {
        # x0 - hard-wired zero
        "zero": RegisterInfo("zero", address_size),
        # x1 - return address (caller saved)
        "ra": RegisterInfo("ra", address_size),
        # x2 - stack pointer (caller saved)
        "sp": RegisterInfo("sp", address_size),
        # x3 - global pointer
        "gp": RegisterInfo("gp", address_size),
        # x4 - threat pointer
        "tp": RegisterInfo("tp", address_size),
        # x5-7 - temporaries (caller saved)
        "t0": RegisterInfo("t0", address_size),
        "t1": RegisterInfo("t1", address_size),
        "t2": RegisterInfo("t2", address_size),
        # x8 - saved register / frame pointer (caller saved)
        "s0": RegisterInfo("s0", address_size),
        # x9 - saved register
        "s1": RegisterInfo("s1", address_size),
        # x10-x11 - first function argument and return value (caller saved)
        "a0": RegisterInfo("a0", address_size),
        "a1": RegisterInfo("a1", address_size),
        # x12-17 - function arguments (caller saved)
        "a2": RegisterInfo("a2", address_size),
        "a3": RegisterInfo("a3", address_size),
        "a4": RegisterInfo("a4", address_size),
        "a5": RegisterInfo("a5", address_size),
        "a6": RegisterInfo("a6", address_size),
        "a7": RegisterInfo("a7", address_size),
        # x18-27 - saved registers (caller saved
        "s2": RegisterInfo("s2", address_size),
        "s3": RegisterInfo("s3", address_size),
        "s4": RegisterInfo("s4", address_size),
        "s5": RegisterInfo("s5", address_size),
        "s6": RegisterInfo("s6", address_size),
        "s7": RegisterInfo("s7", address_size),
        "s8": RegisterInfo("s8", address_size),
        "s9": RegisterInfo("s9", address_size),
        "s10": RegisterInfo("s10", address_size),
        "s11": RegisterInfo("s11", address_size),
        # x28-31 - temporaries
        "t3": RegisterInfo("t3", address_size),
        "t4": RegisterInfo("t4", address_size),
        "t5": RegisterInfo("t5", address_size),
        "t6": RegisterInfo("t6", address_size),
        # pc
        "pc": RegisterInfo("pc", address_size),
    }

    stack_pointer = "sp"

    def get_instruction_info(self, data, addr):

        instr = self.disassembler.decode(data, addr)

        if instr is None:
            return None

        result = InstructionInfo()
        result.length = instr.size

        dest = addr + instr.imm

        if instr.name == 'ret':
            result.add_branch(BranchType.FunctionReturn)
        elif instr.name in branch_ins:
            result.add_branch(BranchType.TrueBranch, dest)
            result.add_branch(BranchType.FalseBranch, addr + 4)
        elif instr.name in direct_call_ins:
            result.add_branch(BranchType.CallDestination, dest)
        elif instr.name in indirect_call_ins:
            result.add_branch(BranchType.UnresolvedBranch)

        return result

    def get_instruction_text(self, data, addr):

        instr = self.disassembler.decode(data, addr)

        if instr is None:
            return None

        tokens = gen_token(instr)

        return tokens, instr.size

    def get_instruction_low_level_il(self, data, addr, il):

        instr = self.disassembler.decode(data, addr)

        if instr is None:
            return None
        self.lifter.lift(il, instr, instr.name)

        return instr.size


class RISCV64(RISCV):
    name = "riscv64"

    address_size = 8
    default_int_size = 8
    max_instr_length = 4

    endianness = Endianness.LittleEndian
    disassembler = RVDisassembler(address_size)
    lifter = Lifter(address_size)

    regs = {k: RegisterInfo(k, 8) for k, v in RISCV.regs.items()}
