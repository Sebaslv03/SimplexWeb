import sympy as sp

class MatrixOperations:
    def __init__(self, matrix):
        # Convert the input matrix to a sympy Matrix
        self.matrix = sp.Matrix(matrix)

    def swap_rows(self, row1, row2):
        self.matrix.row_swap(row1, row2)

    def multiply_row(self, row, scalar):
        self.matrix.row_op(row, lambda v, _: v * scalar)

    def add_multiple_of_row(self, source_row, target_row, scalar):
        self.matrix.row_op(target_row, lambda v, j: v + scalar * self.matrix[source_row, j])

    def swap_columns(self, col1, col2):
        self.matrix.col_swap(col1, col2)

    def multiply_column(self, col, scalar):
        self.matrix.col_op(col, lambda v, _: v * scalar)

    def add_multiple_of_column(self, source_col, target_col, scalar):
        self.matrix.col_op(target_col, lambda v, i: v + scalar * self.matrix[i, source_col])

    def matrix_multiply(self, other_matrix):
        # Convert the other matrix to a sympy Matrix if it's not already
        if not isinstance(other_matrix, sp.Matrix):
            other_matrix = sp.Matrix(other_matrix)
        return self.matrix * other_matrix
    
class SimplexAlgorithm:

    def __init__(self, method, methodSimplex, variables, restricciones, nVariables, nRestricciones, limites):
        self.method = method
        self.methodSimplex = methodSimplex
        self.variables = variables
        self.restricciones = restricciones
        self.nVariables = nVariables
        self.nRestricciones = nRestricciones
        self.artificial = 0
        self.slack = 0
        self.matrix = []
        self.iteraciones = []
        self.rows = []
        self.cols = []
        self.limits = limites
        self.infactible = False
        self.noAcotada = False

    def invertir_signos_y_comparacion(self, lista):
            # Identificar el último número y la comparación
            comparacion = lista[-2]  # penúltimo elemento es la comparación
            ultimo_numero = int(lista[-1])  # último elemento es el número
            # Verificar si el último número es negativo
            if ultimo_numero < 0:
                # Invertir signos de los números
                lista_numeros = [str(-int(num)) for num in lista[:-2]]  # Convertir a entero, cambiar signo, luego de vuelta a string
                # Invertir la comparación
                if comparacion == "<=":
                    comparacion = ">="
                elif comparacion == ">=":
                    comparacion = "<="
                
                # Invertir el signo del último número
                ultimo_numero = -ultimo_numero
                
                # Retornar la lista modificada
                return lista_numeros + [comparacion, str(ultimo_numero)]
            
            # Si no es negativo, devolver la lista original
            return lista

    def dosFases(self):
        # Cuenta de columnas
        cols = int(self.nVariables)+1 #cambiar por variable "variables"
        self.cols.append("BVS")
        auxLimits = []
        indexLimits = 0
        self.nVariables = int(self.nVariables)
        for value in self.limits: 
            if value['type'] == 'sin_limite':
                auxLimits.append(1)
                self.cols.append("X"+str(indexLimits+1)+"p")
                self.cols.append("X"+str(indexLimits+1)+"pp")
                self.nVariables += 1
                cols += 1
            else:
                auxLimits.append(0)
                self.cols.append("X"+str(indexLimits+1))
            indexLimits += 1
        art = 0
        flagArt = False
        slack = 0
        for i in range(len(self.restricciones)): #cambiar por variable "restricciones"
            restriccion = self.invertir_signos_y_comparacion(self.restricciones[i])
            if restriccion[len(restriccion)- 2] == "<=":
                cols += 1
                slack += 1
            elif restriccion[len(restriccion)- 2] == "=":
                cols += 1
                flagArt = True
                art += 1
            else:
                art += 1
                cols += 2
                slack += 1
                flagArt = True
            self.restricciones[i] = restriccion
        rows = int(self.nRestricciones)+1
        aux = art
        self.artificial = art #crear variable artificial
        self.slack = slack #crear variable slack
        # Creación de fila w en caso de que exista
        if flagArt:
            rows += 1
            row = []
            for i in range(0, cols):
                if(i != cols - 1 - aux or aux == 0):
                    row.append(0)   
                else:
                    aux -= 1
                    row.append(1)
            self.matrix.append(row) #cambiar por variable "matrix"
        
        #Creación de la matriz principal
        row = []
        auxFuncion = -1
        
        print(self.method)
        # En caso de minimizar
        if self.method == "minimizar": #cambiar por variable "metodo"
            auxFuncion *= -1
        
        # Creación de la fila de la función objetivo
        index = 0
        for i in range(len(auxLimits)):
            if auxLimits[i] == 1:
                value = self.variables[index]
                if(index + 1 >= len(self.variables)):
                    self.variables.append(value*-1)
                else:
                    self.variables.insert(index+1, value*-1)
                index += 1
            index += 1
        for i in range(0, cols):
            if(i < len(self.variables)):
                row.append(int(self.variables[i]) * auxFuncion)
            else:
                row.append(0)
        self.matrix.append(row)
        
        #Creación de las filas de restricciones
        auxSlack = 0
        auxArt = 0
        totalArt = art
        totalSlack = slack

        count = 0
        for i in range(0, len(auxLimits)):
            if auxLimits[i] == 1:
                count += 1

        for i in range(slack):
            self.cols.append("S" + str(i + 1 + int(self.nVariables) - count))
        for i in range(art):
            self.cols.append("A" + str(i + 1 + int(self.nVariables) - count + slack))

        self.cols.append("RHS")

        index = 0
        for r in self.restricciones:
            row = []
            # Escribimos las variables normales
            for c in range(len(r) - 2):
                row.append(int(r[c]))
                if auxLimits[c] == 1:
                    row.append(-1 * int(r[c]))  
            # Escribimos las variables de holgura o artificial
            if r[len(r)-2] == "<=":
                for i in range(0, auxSlack):
                    row.append(0)
                row.append(1)
                for i in range(0, slack - 1):
                    row.append(0)
                slack -= 1
                auxSlack += 1
                for i in range(0, totalArt):
                    row.append(0)
            elif r[len(r)-2] == ">=":
                for i in range(0, auxSlack):
                    row.append(0)
                row.append(-1)
                for i in range(0, slack - 1):
                    row.append(0)
                slack -= 1
                auxSlack += 1
                for i in range(0, auxArt):
                    row.append(0)
                row.append(1)
                for i in range(0, art - 1):
                    row.append(0)
                art -= 1
                auxArt += 1
            else:
                for i in range(0, totalSlack):
                    row.append(0)
                for i in range(0, auxArt):
                    row.append(0)
                row.append(1)
                for i in range(0, art - 1):
                    row.append(0)
                art -= 1
                auxArt += 1
            row.append(int(r[len(r)-1]))
            self.matrix.append(row)
        auxList = []
        #print(self.matrix)
        if totalArt > 0:
            auxList.append("-W")
        if self.method == "Minimizar":
            auxList.append("-Z")
        else:
            auxList.append("Z")
        for i in range(0, len(self.matrix[0])):
            if self.checkBasic(self.matrix, i, 1):
                for r in range(1, len(self.matrix)):
                    if self.matrix[r][i] == 1:
                        print("indice: "+str(i))
                        print("columna: " + self.cols[i+1])
                        auxList.append(self.cols[i+1])
        self.rows.append(auxList)
        print(self.matrix)
        self.makeArtBasicDosFases()
        #Hacer iteracion de simplex

    def makeArtBasic(self):
            m = MatrixOperations(self.matrix)
            art = self.artificial
            cols = len(self.matrix[0])
            M = sp.symbols('M')
            self.iteraciones.append(self.matrix)
            for i in range(0, art):
                row = 0
                for r in range(0, len(self.matrix)):
                    if(self.matrix[r][cols - art - 1] == 1):
                        art -= 1
                        break
                    row += 1
                m.add_multiple_of_row(row, 0, -M)
            # mostrar iteración
            self.iteraciones.append(m.matrix.tolist())
            self.rows.append(self.rows[0].copy())
            acotada = False
            aIndex = []
            art = self.artificial
            for a in range(0, art):
                aIndex.append(cols - a - 2)
            basic = False
            while any(m.matrix.tolist()[0][i].subs('M', 1000) < 0 for i in range(cols - 1)):
                entry = self.entry(m.matrix.tolist(), cols - self.artificial, 0)
                out = self.ratio(entry, m.matrix.tolist(), 1, 1)
                if (out == -1):
                    acotada = True
                    break
                entryString = self.cols[entry+1]
                auxList = self.rows[-1].copy()
                auxList[out] = entryString
                self.rows.append(auxList)
                self.makeOne(m, out, entry)
                self.makeBasic(m, out, entry)
                # Dibujar Matriz
                self.iteraciones.append(m.matrix.tolist()) ##iteraciones
                basic = False
                for a in range(0, art):
                    basic = self.checkBasic(m.matrix.tolist(), cols - a - 2, 0)
                    if basic:
                        break
            if not any(m.matrix.tolist()[0][i].subs('M', 1000) < 0 for i in range(cols - 1) if i not in aIndex) and basic:
                self.infactible = True
            if acotada:
                self.noAcotada = True
           

            self.matrix = m.matrix.tolist()

    def makeArtBasicDosFases(self):
            m = MatrixOperations(self.matrix)
            art = self.artificial
            cols = len(self.matrix[0])
            self.iteraciones.append(self.matrix)
            
            for i in range(0, art):
                row = 1
                print("aqui")
                print(art)
                for r in range(1, len(self.matrix)):
                    print(self.matrix[r][cols - art - 1])
                    if(self.matrix[r][cols - art - 1] == 1):
                        art -= 1
                        break
                    row += 1
                print(row)
                m.add_multiple_of_row(row, 0, -1)
            row = 0
            z = 0
            art = self.artificial
            aIndex = []
            self.iteraciones.append(m.matrix.tolist())
            self.rows.append(self.rows[0].copy())
            for a in range(0, art):
                aIndex.append(cols - a - 2)
            acotada = False
            basic = False
            jump = 1
            if art > 0:
                jump = 2
            while any(m.matrix.tolist()[row][i] < 0 for i in range(cols - 1) if i not in aIndex):
                entry = self.entry(m.matrix.tolist(), cols - self.artificial, row)
                out = self.ratio(entry, m.matrix.tolist(), jump, jump)
                
                print("entry: " + str(entry))
                print("out: " + str(out))
                if (out == -1):
                    acotada = True
                    break
                entryString = self.cols[entry+1]
                auxList = self.rows[-1].copy()
                auxList[out] = entryString
                self.rows.append(auxList)
                #print("Variables Basicas: " + str(self.rows))
                self.makeOne(m, out, entry)
                self.makeBasic(m, out, entry)
                # si las artificiales son 0 row = 1
                self.iteraciones.append(m.matrix.tolist())
                basic = False
                for a in range(0, art):
                    basic = self.checkBasic(m.matrix.tolist(), cols - a - 2, 0)
                    if basic:
                        break
                if not basic and art > 0:
                    row = 1
                z += 1
                
            if not any(m.matrix.tolist()[row][i] < 0 for i in range(cols - 1) if i not in aIndex) and basic:
                self.infactible = True
            if acotada:
                self.noAcotada = True
            self.matrix = m.matrix.tolist()

    def granM(self):
        # Cuenta de columnas
        cols = int(self.nVariables)+1
        self.cols.append("BVS")
        auxLimits = []
        indexLimits = 0
        self.nVariables = int(self.nVariables)
        for value in self.limits: 
            if value['type'] == 'sin_limite':
                auxLimits.append(1)
                self.cols.append("X"+str(indexLimits+1)+"p")
                self.cols.append("X"+str(indexLimits+1)+"pp")
                self.nVariables += 1
                cols += 1
            else:
                auxLimits.append(0)
                self.cols.append("X"+str(indexLimits+1))
            indexLimits += 1
        art = 0
        flagArt = False
        slack = 0
        for restriccion in self.restricciones:
            restriccion = self.invertir_signos_y_comparacion(restriccion)
            if restriccion[len(restriccion)- 2] == "<=":
                cols += 1
                slack += 1
            elif restriccion[len(restriccion)- 2] == "=":
                cols += 1
                flagArt = True
                art += 1
            else:
                art += 1
                cols += 2
                slack += 1
                flagArt = True
        
        rows = int(self.nRestricciones)+1
        #Creación de la matriz principal
        row = []
        auxFuncion = -1
        M = sp.symbols('M')
        # En caso de minimizar
        if self.method == "minimizar":
            auxFuncion *= -1
        # Creación de la fila de la función objetivo
        print(auxLimits)
        print(self.variables)
        index = 0
        for i in range(len(auxLimits)):
            if auxLimits[i] == 1:
                value = self.variables[index]
                if(index + 1 >= len(self.variables)):
                    self.variables.append(value*-1)
                else:
                    self.variables.insert(index+1, value*-1)
                index += 1
            index += 1
        for i in range(0, self.nVariables):
            if(i < len(self.variables)):
                row.append(int(self.variables[i]) * auxFuncion)
        for i in range(0, slack):
            row.append(0)
        for i in range(0, art):
            row.append(M)
        row.append(0)
        self.matrix.append(row)

        #Creación de las filas de restricciones
        auxSlack = 0
        auxArt = 0
        totalArt = art
        totalSlack = slack
        self.artificial = art
        self.slack = slack

        count = 0
        for i in range(0, len(auxLimits)):
            if auxLimits[i] == 1:
                count += 1

        for i in range(slack):
            self.cols.append("S" + str(i + 1 + int(self.nVariables) - count))
        for i in range(art):
            self.cols.append("A" + str(i + 1 + int(self.nVariables) -count + slack))

        self.cols.append("RHS")

        
        index = 0
        for r in self.restricciones:
            if r[len(r) - 1] < 0:
                for i in range(len(r)):
                    if type(r[i]) != float:
                        if r[i] == "<=":
                            r[i] = ">="
                        elif r[i] == ">=":
                            r[i] = "<="
                    else:
                        r[i] = r[i] * -1

        for r in self.restricciones:
            row = []
            # Escribimos las variables normales
            for c in range(len(r) - 2):
                row.append(int(r[c]))
                if auxLimits[c] == 1:
                    row.append(-1 * int(r[c]))  
            # Escribimos las variables de holgura o artificial
            if r[len(r)-2] == "<=":
                for i in range(0, auxSlack):
                    row.append(0)
                row.append(1)
                for i in range(0, slack - 1):
                    row.append(0)
                slack -= 1
                auxSlack += 1
                for i in range(0, totalArt):
                    row.append(0)
            elif r[len(r)-2] == ">=":
                for i in range(0, auxSlack):
                    row.append(0)
                row.append(-1)
                for i in range(0, slack - 1):
                    row.append(0)
                slack -= 1
                auxSlack += 1
                for i in range(0, auxArt):
                    row.append(0)
                row.append(1)
                for i in range(0, art - 1):
                    row.append(0)
                art -= 1
                auxArt += 1
            else:
                for i in range(0, totalSlack):
                    row.append(0)
                for i in range(0, auxArt):
                    row.append(0)
                row.append(1)
                for i in range(0, art - 1):
                    row.append(0)
                art -= 1
                auxArt += 1
            row.append(int(r[len(r)-1]))
            self.matrix.append(row)
        print(self.matrix)
        auxList = []
        if self.method == "Minimizar":
            auxList.append("-Z")
        else:
            auxList.append("Z")
        for i in range(0, len(self.matrix[0])):
            if self.checkBasic(self.matrix, i, 1):
                for r in range(1, len(self.matrix)):
                    if self.matrix[r][i] == 1:
                        print("indice: "+str(i))
                        auxList.append(self.cols[i+1])
        self.rows.append(auxList)
        self.makeArtBasic()
        


    def checkBasic(self,matrix,col, start):
        ones = 0
        for i in range(start, len(matrix)):
            if(matrix[i][col] == 1):
                ones += 1
            elif(matrix[i][col] != 0):
                return False
        return ones == 1


    def entry(self, matrix, cols, r):
        min_value = float('inf')  # Use Python's infinity
        min_index = -1
        for c in range(0, cols - 1):
            value = matrix[r][c].subs('M', 1000)  # Substitute M with a large number
            if value < min_value:
                min_value = value
                min_index = c
        return min_index

    def ratio(self, entry_index, matrix, jump, r):
        rhs = [row[-1] for row in matrix[jump:]]  # Extract RHS values from the last column, skipping the first row
        print(rhs)
        pivot_column = [row[entry_index] for row in matrix[jump:]]  # Extract pivot column values, skipping the first row
        ratios = []
        for i in range(len(rhs)):
            if pivot_column[i] != 0:
                if pivot_column[i] < 0:
                    ratios.append((float('inf'), i + r))
                else:
                    ratio = rhs[i] / pivot_column[i]
                    if ratio >= 0:  # Only consider non-negative ratios
                        ratios.append((ratio, i + r))  # Adjust index to match the original matrix
            else:
                ratios.append((float('inf'), i + r))  # Avoid division by zero and adjust index
        print(ratios)
        # Find the row index with the minimum ratio
        if len(ratios) == 0:
            return -1
        
        todas_con_inf = all(tupla[0] == float('inf') for tupla in ratios)
        if todas_con_inf:
            return -1
        min_ratio_row = min(ratios, key=lambda x: x[0])[1]
        return min_ratio_row
            
    def makeOne(self, matrix, out, entry):
        matrix.multiply_row(out, 1 / matrix.matrix.tolist()[out][entry])

    def makeBasic(self, matrix, out, entry):
        for r in range(len(matrix.matrix.tolist())):
            if(r != out):
                scalar = -matrix.matrix.tolist()[r][entry]
                matrix.add_multiple_of_row(out, r, scalar)

    def createMatrix(self):
        if(self.methodSimplex == "gran_m"):
            self.granM()
        else:
            self.dosFases()
        return self.iteraciones