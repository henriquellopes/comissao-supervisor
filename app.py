import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Comissão - Supervisor",
    page_icon="👔",
    layout="wide" # Layout expandido para caber as 4 colunas
)

st.title("👔 Calculadora de Comissão - Supervisor")
st.markdown("Insira os valores vendidos por tabela para calcular a remuneração baseada nas faixas de faturamento da equipe.")

# --- DADOS DE ENTRADA (4 COLUNAS) ---
st.subheader("1. Insira o Faturamento por Tabela")

with st.container():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**1. BA, BMA e Est. 2%**")
        st.caption("Multiplicador: 1.0 (Cheia)")
        venda_tab1 = st.number_input("R$", min_value=0.0, step=1000.0, key="t1")

    with col2:
        st.markdown("**2. SELECT, PESADOS**")
        st.caption("Multiplicador: 1.0 (Cheia)")
        venda_tab2 = st.number_input("R$", min_value=0.0, step=1000.0, key="t2")

    with col3:
        st.markdown("**3. Estendida 12x**")
        st.caption("Multiplicador: 0.5 (Metade)")
        venda_tab3 = st.number_input("R$", min_value=0.0, step=1000.0, key="t3")

    with col4:
        st.markdown("**4. Estendida 1%**")
        st.caption("Multiplicador: 0.7 (70%)")
        venda_tab4 = st.number_input("R$", min_value=0.0, step=1000.0, key="t4")

# Botão de Cálculo
st.markdown("---")
calcular = st.button("Calcular Comissão do Supervisor", type="primary")

if calcular:
    # 1. SOMA TOTAL PARA DEFINIR A FAIXA (TIER)
    faturamento_total = venda_tab1 + venda_tab2 + venda_tab3 + venda_tab4
    
    # Definição das Faixas baseada na Imagem do Supervisor
    # Faixa 1: Até 4.8M | Faixa 2: Até 7.5M | Faixa 3: Acima de 7.5M
    
    taxa_total_faixa = 0.0
    split_pagamento = [] # [1º pgto, 2º pgto, 3º pgto] (Percentuais brutos da faixa)

    if faturamento_total <= 4800000:
        nivel = "Faixa 1 (Até 4.8M)"
        taxa_total_faixa = 0.25 # 0.25%
        split_pagamento = [0.16, 0.045, 0.045]
        
    elif faturamento_total <= 7500000:
        nivel = "Faixa 2 (Até 7.5M)"
        taxa_total_faixa = 0.30 # 0.30%
        split_pagamento = [0.16, 0.070, 0.070]
        
    else:
        nivel = "Faixa 3 (Acima de 7.5M)"
        taxa_total_faixa = 0.35 # 0.35%
        split_pagamento = [0.16, 0.070, 0.120]

    # Mostra o cabeçalho do resultado
    st.subheader("📊 Resultado da Safra")
    c_res1, c_res2, c_res3 = st.columns(3)
    c_res1.metric("Faturamento Total da Equipe", f"R$ {faturamento_total:,.2f}")
    c_res2.metric("Faixa Atingida", nivel)
    c_res3.metric("Percentual Base da Faixa", f"{taxa_total_faixa:.2f}%")

    st.divider()

    # 2. CÁLCULO PONDERADO POR TABELA
    # Fórmula: Valor Venda * (Taxa da Faixa * Multiplicador da Tabela)
    
    # Dicionário para facilitar o loop
    # Nome, Valor Vendido, Multiplicador
    tabelas_calc = [
        ("1. BA/BMA/Est.2%", venda_tab1, 1.0),
        ("2. SELECT/PESADOS", venda_tab2, 1.0),
        ("3. Estendida 12x", venda_tab3, 0.5),
        ("4. Estendida 1%", venda_tab4, 0.7),
    ]

    total_comissao_base = 0.0
    
    # Listas para somar os pagamentos parcelados
    total_pgto1 = 0.0
    total_pgto2 = 0.0
    total_pgto3 = 0.0

    st.subheader("💰 Detalhamento por Tabela")
    
    # Cria colunas para mostrar o detalhe de cada tabela
    cols_detalhe = st.columns(4)

    for i, (nome, valor, multi) in enumerate(tabelas_calc):
        with cols_detalhe[i]:
            if valor > 0:
                # Taxa Efetiva = Taxa da Faixa * Multiplicador
                taxa_efetiva = taxa_total_faixa * multi
                comissao_item = valor * (taxa_efetiva / 100)
                
                total_comissao_base += comissao_item
                
                st.info(f"**{nome}**")
                st.write(f"Venda: R$ {valor:,.2f}")
                st.write(f"Mult: **{multi}x**")
                st.write(f"Taxa Real: **{taxa_efetiva:.3f}%**")
                st.success(f"Comissão: **R$ {comissao_item:,.2f}**")
                
                # Cálculo das Parcelas (Proporcional ao split da faixa, mas ajustado pelo multiplicador)
                # Se a comissão caiu pela metade, a parcela cai pela metade também.
                
                # Fatores de proporção dentro da faixa (ex: 0.16 de 0.25 representa 64% do total)
                fator_p1 = split_pagamento[0] / taxa_total_faixa
                fator_p2 = split_pagamento[1] / taxa_total_faixa
                fator_p3 = split_pagamento[2] / taxa_total_faixa
                
                p1_val = comissao_item * fator_p1
                p2_val = comissao_item * fator_p2
                p3_val = comissao_item * fator_p3
                
                total_pgto1 += p1_val
                total_pgto2 += p2_val
                total_pgto3 += p3_val
                
            else:
                st.warning(f"**{nome}**\n\nSem vendas.")

    # 3. RESULTADOS FINAIS COM DSR
    dsr_valor = total_comissao_base * 0.25
    total_final = total_comissao_base + dsr_valor
    
    # Ajusta as parcelas para incluir DSR também (já que o DSR é pago junto)
    total_pgto1_com_dsr = total_pgto1 * 1.25
    total_pgto2_com_dsr = total_pgto2 * 1.25
    total_pgto3_com_dsr = total_pgto3 * 1.25

    st.divider()
    st.header("🏆 Resumo Financeiro do Supervisor")
    
    c_fin1, c_fin2, c_fin3 = st.columns(3)
    c_fin1.metric("Comissão Base (Soma)", f"R$ {total_comissao_base:,.2f}")
    c_fin2.metric("➕ DSR (25%)", f"R$ {dsr_valor:,.2f}")
    c_fin3.metric("💰 TOTAL A RECEBER", f"R$ {total_final:,.2f}", delta="Final")
    
    st.markdown("### 📅 Fluxo de Recebimento (Previsão com DSR)")
    col_fluxo1, col_fluxo2, col_fluxo3 = st.columns(3)
    
    col_fluxo1.info(f"**1º Pagamento (Confirmação):**\nR$ {total_pgto1_com_dsr:,.2f}")
    col_fluxo2.info(f"**2º Pagamento:**\nR$ {total_pgto2_com_dsr:,.2f}")
    col_fluxo3.info(f"**3º Pagamento:**\nR$ {total_pgto3_com_dsr:,.2f}")

# --- RODAPÉ ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888888; font-size: 14px;'>
        Desenvolvido por <b>Edson Lopes</b> | Filial Taboão da Serra
    </div>
    """, 
    unsafe_allow_html=True
)
