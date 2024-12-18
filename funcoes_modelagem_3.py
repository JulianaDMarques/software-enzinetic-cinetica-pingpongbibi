import numpy as np  # Biblioteca para cálculos numéricos
import pandas as pd  # Biblioteca para manipulação de dados
import matplotlib.pyplot as plt  # Biblioteca para plotar gráficos
from scipy.integrate import solve_ivp  # Resolve equações diferenciais
from scipy.optimize import curve_fit  # Ajuste de curvas

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
def funcao_final(file_path, E0):

    #Função da leitura dos dados fornecidos pelo usuário
    def read_data_from_excel(file_path):
        """
        Leitura dos dados de concentração e tempo de substratos a partir de um arquivo Excel.
        """
        data = pd.read_excel(file_path, index_col=None, dtype={'tempo': int, 'Substrato 1': float,  'Substrato 2': float})
        time = data['tempo'].values
        substrate_1 = data['Substrato 1'].values
        substrate_2 = data['Substrato 2'].values
        return time, substrate_1, substrate_2

    time, substrate_1, substrate_2 = read_data_from_excel(file_path)
 
    # Função do modelo cinético
    def kinetic_model(t, k1, k2, k3, k4):
        """Simular os dados com os parâmetros cinéticos."""
        y0 = [E0, substrate_1[0], 0, 0, substrate_2[0], 0, 0, 0] #condições iniciais 
        sol = solve_ivp(eq_dif, [t[0], t[-1]], y0, t_eval=t, args=(k1, k1, k2, k3, k3, k4)) # Resolve EDO
        return sol.y[1], sol.y[4] ## Retorna concentrações simuladas de substratos

    # Ajuste dos parâmetros que serão usados no modelo  
    def calculate_kinetics(time, substrate1, substrate2, E0):
        """Ajustar os parâmetros cinéticos com base nos dados experimentais."""
        def fit_function(t, k1, k2, k3, k4):
            s1, s2 = kinetic_model(t, k1, k2, k3, k4)
            return np.concatenate([s1, s2]) # Junta os resultados para ajuste
    
        # Ajuste das constantes k1, k2, k3, k4
        popt, _ = curve_fit(
            fit_function, time, np.concatenate([substrate1, substrate2]), p0=[0.1, 0.1, 0.1, 0.1], bounds=(0, np.inf)
        )

        # Calcula Km e Vmax
        k1, k2, k3, k4 = popt
        Km_A = (k1 / 2 + k2) / k1 # Cálculo de Km para substrato A
        Km_B = (k3 / 2 + k4) / k3 # Cálculo de Km para substrato B

        Vmax = E0 * min(k2, k4)

        return k1, k2, k3, k4, Km_A, Km_B, Vmax
    
    # Encontrando as constantes necessárias
    k1, k2, k3, k4, Km_A, Km_B, Vmax = calculate_kinetics(time, substrate_1, substrate_2, E0)
    

    # Plotagem dos resultados
    def plot_results(time, substrate1, substrate2, E0, k1, k2, k3, k4):
        #print("Os parâmetros cinéticos calculados com base nos dados experimentais são:")
        #print("k1:", k1," k2:", k2,"k3:", k3, "k4:", k4, "Km_A:",  Km_A , "Km_B:", Km_B, "Vmax:", Vmax)
        """Gerar os gráficos com os resultados simulados e experimentais."""
        y0 = [E0, substrate1[0], 0, 0, substrate2[0], 0, 0, 0]
        sol = solve_ivp(eq_dif, [time[0], time[-1]], y0, t_eval=time, args=(k1, k1, k2, k3, k3, k4))

        # Cálculo da Velocidade
        v = (Vmax * substrate1 * substrate2) / (substrate2 * Km_A + substrate1 * Km_B + substrate1 * substrate2) 
        
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
        plt.title('Concentração (%) x Tempo', fontsize=12, weight='bold')
        plt.xlabel('Tempo (min)', fontsize=10, weight='bold')
        plt.ylabel('Concentração (mol/L)', fontsize=10, weight='bold')
        plt.legend(loc='best')
        plt.grid()

        # Calculo da Conversão vs Tempo
        conversao = 100 * sol.y[7] / substrate2[0]
       
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

    return calculate_kinetics(time, substrate_1, substrate_2, E0), plot_results(time, substrate_1, substrate_2, E0, k1, k2, k3, k4)


    

   

    