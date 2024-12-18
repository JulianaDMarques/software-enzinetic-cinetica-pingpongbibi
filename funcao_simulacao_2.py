import numpy as np  # Biblioteca para cálculos numéricos
import pandas as pd  # Biblioteca para manipulação de dados
import matplotlib.pyplot as plt  # Biblioteca para plotar gráficos
from scipy.integrate import solve_ivp  # Resolve equações diferenciais

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

#Função para plotar gráficos da simulação
def plot_sim(E0,Kcat_a, Kcat_b,s0_a,s0_b,t_input,k1, k_1, k2, k3, k_3, k4):
    
    #Variáveis modelo
    E0 = float(E0)
    s0_a = float(s0_a)
    s0_b = float(s0_b)
    t_input = float(t_input)
    Kcat_a = float(Kcat_a)
    Kcat_b = float(Kcat_b)


    k1 = float(k1)
    k_1 = float(k_1)
    k2 = float(k2)
    k3 = float(k3)
    k_3 = float(k_3)
    k4 = float(k4)


    # Criando o conjunto de dados artificiais -> ARRAY
    n_ptos = int(100)              #Número de pontos experimentais: 100 pontos
    sa = np.linspace(0,s0_a, n_ptos)   #Gera um array com n_ptos de concentração de substrato 1 (s1) de 0 a sa_max
    sb = np.linspace(0,s0_b, n_ptos)   #Gera um array com n_ptos de concentração de substrato 2 (s2) de 0 a sb_max
    Kcat_global = min(Kcat_a, Kcat_b)  # Use o Kcat mais limitante
    Vmax = E0 * Kcat_global              #Cálculo da Velocidade Máxima

    v = modelo(Vmax, k_1, k1, k2, k_3, k4, k3, sa, sb)   #Calcula a velocidade para cada s (concentração) do array através da função modelo
  

    #Concentração por Tempo
    t = np.linspace(0,t_input, n_ptos) #(0 a t_input minutos de reação, minuto a minuto)

    y0 = [E0, s0_a, 0, 0, s0_b, 0, 0, 0] 
    
    # Resolve EDO
    sol = solve_ivp(eq_dif, (t[0],t[-1]), y0, args=(k1, k_1, k2, k3, k_3, k4), dense_output=True)

    # Gera os vetores para os gráficos
    y = sol.sol(t)

    #Calculo da conversão 
    conv_b = f_conversao(s0_b, y[7])

    with np.errstate(divide='ignore', invalid='ignore'):
        inv_v = 1 / v
        inv_sa = 1 / sa
        inv_sb = 1 / sb
    
# #Gráficos
    #Quadrante 1 -> Substratos pela velocidade
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.plot(sa, v, '-', color='firebrick', label='substrato 1', markersize=3)
    plt.plot(sb, v, '--', color='darkorange', label = 'Substrato 2', markersize=3)
    plt.title('Velocidade x Substrato', fontsize=12, weight='bold')
    plt.xlabel('Concentração de Substrato (mol/L)', fontsize=10, weight='bold')
    plt.ylabel('Velocidade (mol/L/min)', fontsize=10, weight='bold')
    plt.legend(loc='best')
    plt.grid()

    #Quadrante 2 -> 1/Velocidade x 1/Substratos
    plt.subplot(2, 2, 2)
    np.seterr(divide='ignore', invalid='ignore')
    plt.plot(inv_sa,inv_v, 'o-', color = 'firebrick',label='substrato 1', markersize=3)
    plt.plot(inv_sb,inv_v, 'o--', color = 'darkorange',label='substrato 2', markersize=3)
    plt.title('Lineweaver-Burk Plot', fontsize=12, weight='bold')
    plt.xlabel('1/[Substrato] (1/mol/L)', fontsize=10, weight='bold')
    plt.ylabel('1/Velocidade (1/(mol/L/min)', fontsize=10, weight='bold')
    plt.legend(loc='best')
    plt.grid()

    #Quadrante 3 -> Concentração (Substrato e Produto) x Tempo
    plt.subplot(2, 2, 3)
    plt.plot(t,y[1], ls='-', color='firebrick', label='Substrato 1')
    plt.plot(t,y[4], ls='--', color='darkorange', label='Substrato 2')
    plt.plot(t,y[6], ls='-.', color='navy', label ='Produto 1')
    plt.plot(t,y[7], ls=':', color='dodgerblue', label ='Produto 2')
    plt.title('Concentração (%) x Tempo', fontsize=12, weight='bold')
    plt.xlabel('Tempo (min)', fontsize=10, weight='bold')
    plt.ylabel('Concentração (mol/L)', fontsize=10, weight='bold')
    plt.legend(loc='best')
    plt.grid()

    #Quadrante 4 -> Conversão x Tempo
    plt.subplot(2, 2, 4)
    plt.plot(t, conv_b, '-', color='seagreen')
    plt.title('Conversão x Tempo', fontsize=12, weight='bold')
    plt.xlabel('Tempo (min)', fontsize=10, weight='bold')
    plt.ylabel('Conversão de Acetato de geranila (%)', fontsize=10, weight='bold')
    plt.legend(loc='best')
    plt.grid()

    plt.tight_layout()
    plt.show()