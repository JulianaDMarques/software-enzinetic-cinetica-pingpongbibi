import numpy as np  # Biblioteca para cálculos numéricos
import pandas as pd  # Biblioteca para manipulação de dados
import matplotlib.pyplot as plt  # Biblioteca para plotar gráficos
from scipy.integrate import solve_ivp  # Resolve equações diferenciais
from scipy.optimize import differential_evolution  # Ajuste de curvas

#Função do modelo
def modelo(Vmax,k_1, k1, k2, k_3, k4, k3, A, B):
    Km_A = (k_1 + k2) / k1 # Cálculo de Km para substrato A
    Km_B = (k_3 + k4) / k3  # Cálculo de Km para substrato B
    v = (Vmax*A*B)/((Km_A*B) + (Km_B*A) + A*B) # Equação da velocidade
    return v

#Calculo da conversão
def f_conversao(s0_b, p_b):
    return ( p_b / s0_b) * 100 # Calcula a conversão como percentual

#Equação diferencial -> Balanço de Massa
def eq_dif(t, y, k1, k_1, k2, k3, k_3, k4):
     # Variáveis de estado (y): E, S1, ES1, E_P1, S2, E_S2, P1, P2
	E, S1, ES1, E_P1, S2, E_S2, P1, P2 = y

    # balanço de massa da reação enzimática ao longo do tempo
	dEdt = -k1 * E * S1 + k_1 * ES1 + k4 * E_S2
	dS1dt = -k1 * E * S1 + k_1 * ES1
	dES1dt = k1 * E * S1 - k_1 * ES1 - k2 * ES1
	dE_P1dt = k2 * ES1 - k3 * E_P1 * S2 + k_3 * E_S2
	dS2dt = -k3 * E_P1 * S2 + k_3 * E_S2
	dE_S2dt = k3 * E_P1 * S2 - k_3 * E_S2 - k4 * E_S2
	dP1dt = k2 * ES1
	dP2dt = k4 * E_S2

	return [dEdt, dS1dt, dES1dt, dE_P1dt, dS2dt, dE_S2dt, dP1dt, dP2dt] # Retorna as taxas de variação

## Função que irá gerar a visualização final da tela e realizará todo o calculo da modelagem
# Essa função precisa do caminho da base de dados que o usuário irá inserir e do valor de E0
def funcao_final(file_path, E0, s0_a, s0_b, adjustments, maxiter, popsize, mutation, recombination):

    #Função da leitura dos dados fornecidos pelo usuário
    def read_data_from_excel(file_path):
        """
        Leitura dos dados de concentração e tempo de substratos a partir de um arquivo Excel.
        """
        data = pd.read_excel(file_path, index_col=None, dtype={'tempo': int,  'Produto 1': float,  'Produto 2': float})
        time = data['tempo'].values
        #substrate_1 = data['Substrato 1'].fillna(0).values
        substrate_1 = s0_a
        substrate_2 = s0_b
        #substrate_2 = data['Substrato 2'].fillna(0).values
        produto_1 = data['Produto 1'].fillna(0).values
        produto_2 = data['Produto 2'].fillna(0).values
        return time, substrate_1, substrate_2, produto_1, produto_2

    time, substrate_1, substrate_2, produto_1, produto_2 = read_data_from_excel(file_path)
 
    # Função do modelo cinético
    def kinetic_model(t, k_params):
        """Simular os dados com os parâmetros cinéticos."""
        k1, k_1, k2, k3, k_3, k4 = k_params
        y0 = [E0, substrate_1, 0, 0, substrate_2, 0, produto_1[0], produto_2[0]] #condições iniciais 
        sol = solve_ivp(eq_dif, [t[0], t[-1]], y0, t_eval=t, args=k_params) # Resolve EDO
        return sol ## Retorna vetores ao longo do tempo com o resultado da EDO

    # Ajuste dos parâmetros que serão usados no modelo 
    def ajustar_parametros(time, produto_1, produto_2):
        def calculate_kinetics(time, produto_1, produto_2):
            """Ajustar os parâmetros cinéticos com base nos dados experimentais."""
                    
            # def objetivo(params):
            #     k1, k_1, k2, k3, k_3, k4 = params
            #     k_params = (k1, k_1, k2, k3, k_3, k4)
            #     sol = kinetic_model(time, k_params)
            #     erro_P1 = np.sum((sol.y[6] - produto_1) ** 2)
            #     erro_P2 = np.sum((sol.y[7] - produto_2) ** 2)
            #     return erro_P1 + erro_P2

            def objetivo(params):
                k1, k_1, k2, k3, k_3, k4 = params
                k_params = (k1, k_1, k2, k3, k_3, k4)
                sol = kinetic_model(time, k_params)
                
                errors = []
                if adjustments.get("S1_adjust", False):
                    erro_S1 = np.sum((sol.y[1] - substrate_1) ** 2)
                    errors.append(erro_S1)
                if adjustments.get("S2_adjust", False):
                    erro_S2 = np.sum((sol.y[4] - substrate_2) ** 2)
                    errors.append(erro_S2)
                if adjustments.get("P1_adjust", False):
                    erro_P1 = np.sum((sol.y[6] - produto_1) ** 2)
                    errors.append(erro_P1)
                if adjustments.get("P2_adjust", False):
                    erro_P2 = np.sum((sol.y[7] - produto_2) ** 2)
                    errors.append(erro_P2)
                
                if errors:
                    return sum(errors)  
                else:
                    return None

            bounds = [(0.01, 10)] * 6  # Limites para os parâmetros

            result = differential_evolution(objetivo, bounds, maxiter=maxiter, popsize=popsize, mutation=mutation, recombination=recombination)

            return result.x
    
        # Calcula Km e Vmax
        k1, k_1, k2, k3, k_3, k4 = calculate_kinetics(time, produto_1, produto_2)
        Km_A = (k_1 + k2) / k1 # Cálculo de Km para substrato A
        Km_B = (k_3 + k4) / k3 # Cálculo de Km para substrato B
        Vmax = E0 * min(k2,k4)            #Cálculo da Velocidade Máxima
    
        return k1, k_1, k2, k3, k_3, k4, Km_A, Km_B, Vmax

    # Encontrando as constantes necessárias
    k1, k_1, k2, k3, k_3, k4, Km_A, Km_B, Vmax = ajustar_parametros(time, produto_1, produto_2)
    

    # Plotagem dos resultados
    def plot_results(time, k1, k_1, k2, k3, k_3, k4):
        #print("Os parâmetros cinéticos calculados com base nos dados experimentais são:")
        #print("k1:", k1," k2:", k2,"k3:", k3, "k4:", k4, "Km_A:",  Km_A , "Km_B:", Km_B, "Vmax:", Vmax)
        """Gerar os gráficos com os resultados simulados e experimentais."""
        y0 = [E0, substrate_1, 0, 0, substrate_2, 0, 0, 0]
        sol = solve_ivp(eq_dif, [time[0], time[-1]], y0, t_eval=time, args=(k1, k_1, k2, k3, k_3, k4))

        # Cálculo da Velocidade
        #v = (Vmax * substrate1 * substrate2) / (substrate2 * Km_A + substrate1 * Km_B + substrate1 * substrate2) 
        v = (Vmax * sol.y[1] * sol.y[4]) / (sol.y[4] * Km_A + sol.y[1] * Km_B + sol.y[1] * sol.y[4]) 
        
        ## Gráfico da Velocidade x Substrato
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.plot(sol.y[1], v, '-', color='firebrick', label='substrato 1', markersize=3)
        plt.plot(sol.y[4], v, '--', color='darkorange', label = 'Substrato 2', markersize=3)
        plt.title('Velocidade x Substrato', fontsize=12, weight='bold')
        plt.xlabel('Concentração de Substrato (mol/L)', fontsize=10, weight='bold')
        plt.ylabel('Velocidade (mol/L/min)', fontsize=10, weight='bold')
        plt.legend(loc='best')
        plt.grid()

        # Lineweaver-Burk
        inv_v = 1 / v
        inv_s1 = 1 / sol.y[1]
        inv_s2 = 1 / sol.y[4]
        
        ## Gráfico da Lineweaver-Burk x Substrato
        plt.subplot(2, 2, 2)
        np.seterr(divide='ignore', invalid='ignore')
        plt.plot(inv_s1, inv_v, 'o-', color = 'firebrick',label='substrato 1', markersize=3)
        plt.plot(inv_s2, inv_v, 'o--', color = 'darkorange',label='substrato 2', markersize=3)
        plt.title('Lineweaver-Burk Plot', fontsize=12, weight='bold')
        plt.xlabel('1/[Substrato] (1/mol/L)', fontsize=10, weight='bold')
        plt.ylabel('1/Velocidade (1/(mol/L/min)', fontsize=10, weight='bold')
        plt.legend(loc='best')
        plt.grid()

        ## Gráfico da Concentração do Substrato e Produto pelo Tempo
        plt.subplot(2, 2, 3)
        plt.plot(time, sol.y[1], ls='-', color='firebrick', label='Substrato 1')
        plt.plot(time, sol.y[4], ls='--', color='darkorange', label='Substrato 2')
        plt.plot(time, sol.y[6], ls='-.', color='navy', label ='Produto 1')
        plt.plot(time, sol.y[7], ls=':', color='dodgerblue', label ='Produto 2')
        plt.scatter(time, produto_1, color='navy', marker='o', label='Produto 1 (experimental)')
        plt.scatter(time, produto_2, color='dodgerblue', marker='s', label='Produto 2 (experimental)')
        plt.title('Concentração x Tempo', fontsize=12, weight='bold')
        plt.xlabel('Tempo (min)', fontsize=10, weight='bold')
        plt.ylabel('Concentração (mol/L)', fontsize=10, weight='bold')
        plt.legend(loc='best')
        plt.grid()

        # Calculo da Conversão vs Tempo
        conversao = 100 * sol.y[7] / substrate_2
           
        #Gráfico da Concentração pelo tempo
        plt.subplot(2, 2, 4)
        plt.plot(time, conversao, '-', color='seagreen')
        plt.title('Conversão x Tempo', fontsize=12, weight='bold')
        plt.xlabel('Tempo (min)', fontsize=10, weight='bold')
        plt.ylabel('Conversão de Acetato de geranila (%)', fontsize=10, weight='bold')
        plt.legend(loc='best')
        plt.grid()

        plt.tight_layout()
        plt.show()

    return ajustar_parametros(time, produto_1, produto_2), plot_results(time, k1, k_1, k2, k3, k_3, k4)


    

   

    