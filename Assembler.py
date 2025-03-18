import sys

DEBUG = False

inputline = []
err = []
mc = []
opcodes = {
    "add": "00000", "sub": "00001", "mul": "00010", "div": "00011",
    "mod": "00100", "cmp": "00101", "and": "00110", "or": "00111",
    "not": "01000", "mov": "01001",
    "lsl": "01010", "lsr": "01011", "asr": "01100", "nop": "01101",
    "ld": "01110", "st": "01111", "beq": "10000", "bgt": "10001",
    "b": "10010", "call": "10011", "ret": "10100", "hlt": "11111"
}
reg = {
    "r1": "0001", "r2": "0010", "r3": "0011", "r4": "0100",
    "r5": "0101", "r6": "0110", "r7": "0111", "r8": "1000",
    "r9": "1001", "r10": "1010", "r11": "1011", "r12": "1100",
    "r13": "1101", "r14": "1110", "r0": "0000"
}
instrType = {
    "nop": 0, "ret": 0, "hlt": 0, "call": 1, "b": 1, "beq": 1,
    "bgt": 1, "add": 3, "addh": 3, "addu": 3, "sub": 3, "subh": 3,
    "subu": 3, "mul": 3, "mulh": 3, "mulu": 3, "div": 3, "divh": 3,
    "divu": 3, "mod": 3, "modh": 3, "modu": 3, "or": 3, "orh": 3,
    "oru": 3, "lsl": 3, "lslh": 3, "lslu": 3, "lsr": 3, "lsrh": 3,
    "lsru": 3, "asr": 3, "asrh": 3, "asru": 3, "cmp": 2, "not": 2,
    "noth": 2, "notu": 2, "and": 3, "andh": 3, "andu": 3, "mov": 2,
    "movh": 2, "movu": 2, "ld": 4, "st": 4
}
label = {}

def logError(msg):
    err.append(msg)
    if DEBUG:
        print(msg)

def parser(l):
    ns = 0
    t = ""
    for i in range(len(l)):
        if l[i] == ' ' and ns == 0:
            t += l[i]
            ns += 1
            continue
        if l[i] == ',':
            t += ' '
            continue
        if l[i] == '/' or l[i] == ';':
            break
        t += l[i]
    return t

def en(s):
    st = 0
    while st < len(s) and not (s[st].isdigit() or s[st] == '-'):
        st += 1
    return s[st:]

def inb(num, n):
    ans = ['0'] * n
    for i in range(n - 1, -1, -1):
        if num % 2 == 1:
            ans[i] = '1'
        else:
            ans[i] = '0'
        num //= 2
    return "".join(ans)

def tc(num):
    bs = ""
    in_val = 0
    if num < 0:
        num = -num
        in_val = 1
    while num != 0:
        if num % 2 == 0:
            bs = "0" + bs
        else:
            bs = "1" + bs
        num //= 2
    while len(bs) < 27:
        bs = "0" + bs
    if in_val:
        bs_list = list(bs)
        for i in range(27):
            bs_list[i] = '1' if bs_list[i] == '0' else '0'
        bs = "".join(bs_list)
        c = 1
        bs_list = list(bs)
        for i in range(26, -1, -1):
            bit = 1 if bs_list[i] == '1' else 0
            bs_list[i] = chr((bit + c) % 2 + ord('0'))
            c = (bit + c) // 2
        bs = "".join(bs_list)
    return bs

def hti(hexStr):
    result = 0
    base_val = 1
    if hexStr[:2] == "0x" or hexStr[:2] == "0X":
        hexStr = hexStr[2:]
    for i in range(len(hexStr) - 1, -1, -1):
        c = hexStr[i]
        digit = 0
        if '0' <= c <= '9':
            digit = ord(c) - ord('0')
        elif 'A' <= c <= 'F':
            digit = ord(c) - ord('A') + 10
        elif 'a' <= c <= 'f':
            digit = ord(c) - ord('a') + 10
        result += digit * base_val
        base_val *= 16
    return result

def main():
    global inputline, err, mc, opcodes, reg, instrType, label
    try:
        inputfile = open("input.txt", "r")
    except:
        logError("Error: File Could Not Be Opened.")
        return 1
    else:
        print("File Opened Successfully.")
        for line in inputfile:
            inputline.append(line.rstrip("\n"))
    inputfile.close()
    if DEBUG:
        print("File Opened Successfully. Total lines:", len(inputline))
    for i in range(len(inputline)):
        inputline[i] = parser(inputline[i])
        if DEBUG:
            print("After parsing, line", i + 1, ":", inputline[i])
    for i in range(len(inputline)):
        tokens = inputline[i].split()
        for token in tokens:
            if ':' in token:
                if token[-1] == ':':
                    labelName = token[:-1]
                    label[labelName] = i + 1
                    if DEBUG:
                        print("Label found:", labelName, "at line", i + 1)
    for i in range(len(inputline)):
        ss = inputline[i].split()
        tokens = []
        for token in ss:
            if ':' not in token:
                tokens.append(token)
            elif token[-1] == ':':
                label[token[:-1]] = i + 1
        if len(tokens) == 0:
            continue

        op = tokens[0].lower()
        type_val = instrType[op]
        ans = ""

        if type_val == 0:
            opp = opcodes[op]
            ans += opp
            while len(ans) < 32:
                ans += '0'
            mc.append(ans)
        elif type_val == 1:
            opp = opcodes[op]
            ans += opp
            op1 = tokens[1]
            g = False
            if op1[0] == '0' and (op1[1] == 'x' or op1[1] == 'X'):
                label[op1] = hti(op1)
                g = True
            y = -i + label[op1]
            off = tc(y)
            if g:
                off = tc(label[op1])
            ans += off
            mc.append(ans)
        elif type_val == 2:
            if len(tokens) < 3:
                logError("Error: Not enough operands for " + op)
                continue
            opp = opcodes[op]
            op1 = tokens[1]
            op2 = tokens[2]
            if op1 not in reg:
                logError("Unknown register: " + op1)
                continue
            if op2[0] == 'r' or op2[0] == 'R':
                ans += opp
                ans += '0'
                ans += reg[op1]
                ans += "0000"
                ans += reg[op2]
                while len(ans) < 32:
                    ans += '0'
                mc.append(ans)
            else:
                mod = "00"
                if len(op) == 4:
                    if op[3] == 'u':
                        mod = "01"
                    else:
                        mod = "10"
                    opp = op[:-1]
                else:
                    opp = tokens[0]
                ans += opcodes[opp]
                ans += '1'
                ans += reg[op1]
                ans += "0000"
                u = en(op2)
                if u == "":
                    logError("Error: No numeric part found in operand: " + op2)
                    continue
                k = int(u, 0)
                imm = inb(k, 16)
                ans += mod
                ans += imm
                mc.append(ans)
        elif type_val == 3:
            if len(tokens) < 4:
                logError("Error: Not enough operands for " + op)
                continue
            op = tokens[0]
            op1 = tokens[1]
            op2 = tokens[2]
            op3 = tokens[3]
            if op1 not in reg:
                logError("Unknown register: " + op1)
                continue
            if op3[0] == 'r' or op3[0] == 'R':
                if op3 not in reg:
                    logError("Unknown register: " + op3)
                    continue
                opp2 = opcodes[op]
                ans += opp2
                ans += '0'
                ans += reg[op1]
                ans += reg[op2]
                ans += reg[op3]
                while len(ans) < 32:
                    ans += '0'
                mc.append(ans)
            else:
                mod = "00"
                if len(op) == 4:
                    if op[3] == 'u':
                        mod = "01"
                    else:
                        mod = "10"
                    opp2 = op[:-1]
                else:
                    opp2 = op
                ans += opcodes[opp2]
                ans += '1'
                ans += reg[op1]
                ans += reg[op2]
                u = en(op3)
                if u == "":
                    logError("Error: No numeric part found in operand: " + op3)
                else:
                    k = int(u, 0)
                    imm = inb(k, 16)
                    ans += mod
                    ans += imm
                    mc.append(ans)
        elif type_val == 4:
            if len(tokens) < 3:
                logError("Error: Not enough operands for " + op)
                continue
            rd = tokens[1]
            imv = tokens[2]
            lb = imv.find('[')
            rb = imv.find(']')
            if lb == -1 or rb == -1:
                logError("Error: Memory operand format error in: " + inputline[i])
                continue
            imm = imv[:lb]
            rs1 = imv[lb + 1:rb]
            if rd not in reg or rs1 not in reg:
                logError("Unknown register in memory operand: " + inputline[i])
                continue
            num = en(imm)
            if num == "":
                logError("Error: No numeric part found in immediate operand: " + imm)
                continue
            immv = int(num, 0)
            imb = inb(immv, 4)
            roi = "1"
            ans = opp + roi + reg[rd] + reg[rs1]
            x = 14
            while x > 0:
                ans += '0'
                x -= 1
            ans += imb
            mc.append(ans)
    for i in range(len(mc)):
        print(mc[i])
    try:
        hexfile = open("hexfile.hex", "w")
    except:
        logError("Error: Could not create hexfile.hex!")
        return 1
    for mc_line in mc:
        val = 0
        base_val = 1
        for j in range(len(mc_line) - 1, -1, -1):
            if mc_line[j] == '1':
                val += base_val
            base_val *= 2
        ans_hex = ""
        if val == 0:
            ans_hex = "0"
        while val > 0:
            r = val % 16
            if r < 10:
                ans_hex = chr(r + ord('0')) + ans_hex
            else:
                ans_hex = chr(r - 10 + ord('A')) + ans_hex
            val //= 16
        while len(ans_hex) < 8:
            ans_hex = "0" + ans_hex
        hexfile.write(ans_hex + "\n")
    hexfile.close()
    print("Machine code stored in hexfile.hex")
    if len(err) > 0:
        print("Errors encountered during assembly")
        for e in err:
            print(e)
    return 0

if __name__ == '__main__':
    main()
