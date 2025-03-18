import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFileDialog)

opcodes = {
    "add": "00000", "sub": "00001", "mul": "00010", "div": "00011",
    "mod": "00100", "cmp": "00101", "and": "00110", "or": "00111",
    "not": "01000", "mov": "01001", "lsl": "01010", "lsr": "01011",
    "asr": "01100", "nop": "01101", "ld": "01110", "st": "01111",
    "beq": "10000", "bgt": "10001", "b": "10010", "call": "10011",
    "ret": "10100", "hlt": "11111"
}
reg = {
    "r1": "0001", "r2": "0010", "r3": "0011", "r4": "0100",
    "r5": "0101", "r6": "0110", "r7": "0111", "r8": "1000",
    "r9": "1001", "r10": "1010", "r11": "1011", "r12": "1100",
    "r13": "1101", "r14": "1110", "r15": "1111"
}
instrType = {
    "nop": 0, "ret": 0, "hlt": 0,
    "call": 1, "b": 1, "beq": 1, "bgt": 1,
    "add": 3, "addh": 3, "addu": 3,
    "sub": 3, "subh": 3, "subu": 3,
    "mul": 3, "mulh": 3, "mulu": 3,
    "div": 3, "divh": 3, "divu": 3,
    "mod": 3, "modh": 3, "modu": 3,
    "or": 3, "orh": 3, "oru": 3,
    "lsl": 3, "lslh": 3, "lslu": 3,
    "lsr": 3, "lsrh": 3, "lsru": 3,
    "asr": 3, "asrh": 3, "asru": 3,
    "cmp": 2, "not": 2, "noth": 2, "notu": 2,
    "and": 3, "andh": 3, "andu": 3,
    "mov": 2, "movh": 2, "movu": 2,
    "ld": 4, "st": 4
}

def parser(line):
    ns = 0
    t = ""
    for ch in line:
        if ch == ' ' and ns == 0:
            t += ch
            ns += 1
            continue
        if ch == ',':
            t += ' '
            continue
        if ch == '/' or ch == ';':
            break
        t += ch
    return t

def en(s):
    st = 0
    while st < len(s) and not (s[st].isdigit() or s[st] == '-'):
        st += 1
    return s[st:]

def inb(num, n):
    return format(num, '0{}b'.format(n))

def tc(num):
    bits = 27
    if num < 0:
        num = (1 << bits) + num
    return format(num, '0{}b'.format(bits))

def hti(hexStr):
    if hexStr.lower().startswith("0x"):
        hexStr = hexStr[2:]
    return int(hexStr, 16)

def assembleCode(input_text):
   
    inputline = []
    machinecode = []
    errorContainer = []
    label = {}

    def logError(msg):
        errorContainer.append(msg)
    lines = input_text.splitlines()
    for line in lines:
        inputline.append(line)
    for i in range(len(inputline)):
        inputline[i] = parser(inputline[i])
    for i in range(len(inputline)):
        tokens = inputline[i].split()
        for token in tokens:
            if token.endswith(':'):
                label[token[:-1]] = i + 1
    for i in range(len(inputline)):
        tokens = []
        for token in inputline[i].split():
            if ':' not in token:
                tokens.append(token)
            elif token.endswith(':'):
                label[token[:-1]] = i + 1
        if not tokens:
            continue
        op = tokens[0].lower()
        if op in opcodes:
            base_op = op
        elif op.endswith('u') and op[:-1] in opcodes:
            base_op = op[:-1]
        elif op.endswith('h') and op[:-1] in opcodes:
            base_op = op[:-1]
        else:
            logError("Unknown opcode: " + op)
            continue
        opp = opcodes[base_op]
        if op not in instrType:
            logError("Unknown instruction type for: " + op)
            continue
        type_val = instrType[op]
        ans = ""

        if type_val == 0:
            ans += opp
            ans = ans.ljust(32, '0')
            machinecode.append(ans)
        elif type_val == 1:
            ans += opp
            op1 = tokens[1]
            g = False
            if op1.startswith("0") and len(op1) > 1 and op1[1] in "xX":
                try:
                    label[op1] = hti(op1)
                    g = True
                except Exception:
                    logError("Invalid hex operand: " + op1)
                    continue
            if op1 not in label:
                logError("Undefined label: " + op1)
                continue
            y = -i + label[op1]
            off = tc(y)
            if g:
                off = tc(label[op1])
            ans += off
            machinecode.append(ans)
        elif type_val == 2:
            if len(tokens) < 3:
                logError("Error: Not enough operands for " + op)
                continue
            op1 = tokens[1]
            op2 = tokens[2]
            if op1 not in reg:
                logError("Unknown register: " + op1)
                continue
            if op2[0].lower() == 'r':
                ans += opp + "0" + reg[op1] + "0000" + reg.get(op2.lower(), "")
                ans = ans.ljust(32, '0')
                machinecode.append(ans)
            else:
                mod = "00"
                if len(op) == len(base_op) + 1:
                    mod = "01" if op[-1] == 'u' else "10"
                    opp = opcodes[base_op]
                else:
                    opp = tokens[0]
                ans += opp
                ans += "1" + reg[op1] + "0000"
                u = en(op2)
                if u == "":
                    logError("Error: No numeric part found in operand: " + op2)
                    continue
                try:
                    k = int(u, 0)
                except Exception:
                    logError("Invalid numeric operand: " + op2)
                    continue
                imm = inb(k, 16)
                ans += mod + imm
                machinecode.append(ans)
        elif type_val == 3:
            if len(tokens) < 4:
                logError("Error: Not enough operands for " + op)
                continue
            op1 = tokens[1]
            op2 = tokens[2]
            op3 = tokens[3]
            if op1 not in reg:
                logError("Unknown register: " + op1)
                continue
            if op3[0].lower() == 'r':
                if op3.lower() not in reg:
                    logError("Unknown register: " + op3)
                    continue
                opp2 = opcodes[op] if op in opcodes else opcodes[base_op]
                ans += opp2 + "0" + reg[op1] + reg[op2] + reg[op3.lower()]
                ans = ans.ljust(32, '0')
                machinecode.append(ans)
            else:
                mod = "00"
                if len(op) == len(base_op) + 1:
                    mod = "01" if op[-1] == 'u' else "10"
                    opp2 = opcodes[base_op]
                else:
                    opp2 = op
                ans += opp2 + "1" + reg[op1] + reg[op2]
                u = en(op3)
                if u == "":
                    logError("Error: No numeric part found in operand: " + op3)
                    continue
                try:
                    k = int(u, 0)
                except Exception:
                    logError("Invalid numeric operand: " + op3)
                    continue
                imm = inb(k, 16)
                ans += mod + imm
                machinecode.append(ans)
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
            rs1 = imv[lb+1:rb]
            if rd not in reg or rs1 not in reg:
                logError("Unknown register in memory operand: " + inputline[i])
                continue
            num = en(imm)
            if num == "":
                logError("Error: No numeric part found in immediate operand: " + imm)
                continue
            try:
                immv = int(num, 0)
            except Exception:
                logError("Invalid immediate operand: " + imm)
                continue
            imb = inb(immv, 4)
            roi = "1"
            ans = opcodes[op] + roi + reg[rd] + reg[rs1]
            ans += "0" * 14
            ans += imb
            machinecode.append(ans)
    hexCode = []
    try:
        # Write to a default hex file (this can be bypassed with the Output File button)
        with open("hexfile.hex", "w") as f:
            for mc in machinecode:
                value = int(mc, 2)
                hexValue = format(value, 'X').upper().zfill(8)
                f.write(hexValue + "\n")
                hexCode.append(hexValue)
    except Exception:
        errorContainer.append("Error: Could not create hexfile.hex!")
    
    return {"binaryCode": machinecode, "hexCode": hexCode, "errors": errorContainer}

class AssemblerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Create text edit widgets with individual styles
        self.inputEdit = QPlainTextEdit(self)
        self.inputEdit.setStyleSheet("background-color: #fff9c4; color: #000; font-family: monospace;")
        self.binaryEdit = QPlainTextEdit(self)
        self.binaryEdit.setStyleSheet("background-color: #c8e6c9; color: #000; font-family: monospace;")
        self.hexEdit = QPlainTextEdit(self)
        self.hexEdit.setStyleSheet("background-color: #bbdefb; color: #000; font-family: monospace;")
        self.debugEdit = QPlainTextEdit(self)
        self.debugEdit.setStyleSheet("background-color: #ffcdd2; color: #000; font-family: monospace;")
        
        self.binaryEdit.setReadOnly(True)
        self.hexEdit.setReadOnly(True)
        self.debugEdit.setReadOnly(True)
        
        # Create labels with some color styling
        inputLabel = QLabel("Input Code", self)
        inputLabel.setStyleSheet("font-weight: bold; color: #f57c00;")
        binaryLabel = QLabel("Binary Output", self)
        binaryLabel.setStyleSheet("font-weight: bold; color: #388e3c;")
        hexLabel = QLabel("Hex Output", self)
        hexLabel.setStyleSheet("font-weight: bold; color: #1976d2;")
        debugLabel = QLabel("Debug Output", self)
        debugLabel.setStyleSheet("font-weight: bold; color: #d32f2f;")
        
        # Create buttons with colorful styles
        self.loadButton = QPushButton("Load File", self)
        self.loadButton.setStyleSheet("background-color: #3F51B5; color: white; padding: 10px; border-radius: 5px;")
        self.runButton = QPushButton("Run", self)
        self.runButton.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.debugButton = QPushButton("Debug", self)
        self.debugButton.setStyleSheet("background-color: #FF9800; color: white; padding: 10px; border-radius: 5px;")
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 5px;")
        self.outputButton = QPushButton("Output File", self)
        self.outputButton.setStyleSheet("background-color: #009688; color: white; padding: 10px; border-radius: 5px;")
        
        # Set overall window style (background color and font)
        self.setStyleSheet("background-color: #e1f5fe; font-family: Arial;")
        
        # Connect button signals to slots
        self.loadButton.clicked.connect(self.onLoadClicked)
        self.runButton.clicked.connect(self.onRunClicked)
        self.debugButton.clicked.connect(self.onDebugClicked)
        self.clearButton.clicked.connect(self.onClearClicked)
        self.outputButton.clicked.connect(self.onOutputClicked)
        
        # Layout for input section
        inputLayout = QVBoxLayout()
        inputLayout.addWidget(inputLabel)
        inputLayout.addWidget(self.inputEdit)
        
        # Layout for binary output
        binaryLayout = QVBoxLayout()
        binaryLayout.addWidget(binaryLabel)
        binaryLayout.addWidget(self.binaryEdit)
        
        # Layout for hex output
        hexLayout = QVBoxLayout()
        hexLayout.addWidget(hexLabel)
        hexLayout.addWidget(self.hexEdit)
        
        # Layout for debug output
        debugLayout = QVBoxLayout()
        debugLayout.addWidget(debugLabel)
        debugLayout.addWidget(self.debugEdit)
        
        # Layout for buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.loadButton)
        buttonLayout.addWidget(self.runButton)
        buttonLayout.addWidget(self.debugButton)
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addWidget(self.outputButton)
        
        # Grid layout to organize all sections
        gridLayout = QGridLayout()
        gridLayout.addLayout(inputLayout, 0, 0)
        gridLayout.addLayout(binaryLayout, 0, 1)
        gridLayout.addLayout(hexLayout, 1, 0)
        gridLayout.addLayout(debugLayout, 1, 1)
        gridLayout.addLayout(buttonLayout, 2, 0, 1, 2)
        
        self.setLayout(gridLayout)
        self.setWindowTitle("Assembler GUI")
        self.resize(900, 650)
    
    def onLoadClicked(self):
        # Open a file dialog to select an assembly file to load
        filename, _ = QFileDialog.getOpenFileName(self, "Open Assembly File", "",
                                                  "Assembly Files (*.asm *.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, "r") as f:
                    file_contents = f.read()
                self.inputEdit.setPlainText(file_contents)
            except Exception as e:
                self.debugEdit.appendPlainText("Error reading file: " + str(e))
    
    def onRunClicked(self):
        inputCode = self.inputEdit.toPlainText()
        result = assembleCode(inputCode)
        self.binaryEdit.clear()
        self.hexEdit.clear()
        for line in result["binaryCode"]:
            self.binaryEdit.appendPlainText(line)
        for line in result["hexCode"]:
            self.hexEdit.appendPlainText(line)
        self.debugEdit.clear()
    
    def onDebugClicked(self):
        inputCode = self.inputEdit.toPlainText()
        result = assembleCode(inputCode)
        self.debugEdit.clear()
        if not result["errors"]:
            self.debugEdit.appendPlainText("No errors found.")
        else:
            for line in result["errors"]:
                self.debugEdit.appendPlainText(line)
    
    def onClearClicked(self):
        self.inputEdit.clear()
    
    def onOutputClicked(self):
        # Assemble the code and then prompt the user to save the hex output
        inputCode = self.inputEdit.toPlainText()
        result = assembleCode(inputCode)
        if result["errors"]:
            self.debugEdit.appendPlainText("Assembly errors: " + "; ".join(result["errors"]))
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save Hex Output", "",
                                                  "Hex Files (*.hex *.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, "w") as f:
                    for hex_line in result["hexCode"]:
                        f.write(hex_line + "\n")
                self.debugEdit.appendPlainText("Hex output saved to " + filename)
            except Exception as e:
                self.debugEdit.appendPlainText("Error saving file: " + str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AssemblerGUI()
    window.show()
    sys.exit(app.exec_())
