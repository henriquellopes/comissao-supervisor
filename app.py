import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Simulador Supervisor - Parcelado",
    page_icon="👔",
    layout="wide"
)

st.title("👔 Calculadora de Comissão - Supervisor")
st.markdown("Cálculo detalhado com validação de totais e quebra por parcelas de pagamento.")

# --- 1. VALIDAÇÃO DE SEGURANÇA ---
st.header("1. Validação de Totais")
col_val1, col_val2 = st.columns([1, 2])
with col_val1:
    meta_informada = st.number_input(
        "Insira o VALOR TOTAL de todas as vendas (para conferência):", 
        min_value=0.0, step=1000.0, format="%.2f"
    )

# --- 2. DADOS DE ENTRADA POR TABELA ---
st.header("2. Detalhamento por Tabela")

with st.container():
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.info("**1. BA, BMA e Est. 2%**")
        st.caption("Multiplicador: 1.0")
        v_tab1 = st.number_input("R$", min_value=0.0, step=1000.0, key="t1")

    with c2:
        st.info("**2. SELECT, PESADOS**")
        st.caption("Multiplicador: 1.0")
        v_tab2 = st.number_input("R$", min_value=0.0, step=1000.0, key="t2")

    with c3:
        st.warning("**3. Estendida 12x**")
        st.caption("Multiplicador: 0.5 (50%)")
        v_tab3 = st.number_input("R$", min_value=0.0, step=1000.0, key="t3")

    with c4:
        st.error("**4. Estendida 1%**")
        st.caption("Multiplicador: 0.7 (70%)")
        v_tab4 = st.number_input("R$", min_value=0.0, step=1000.0, key="t4")

# --- LÓGICA DE VALIDAÇÃO VISUAL ---
soma_tabelas = v_tab1 + v_tab2 + v_tab3 + v_tab4
diferenca = meta_informada - soma_tabelas

st.markdown("---")
col_check1, col_check2 = st.columns(2)
col_check1.metric("Total Informado", f"R$ {meta_informada:,.2f}")
col_check2.metric(
    "Soma das Tabelas", 
    f"R$ {soma_tabelas:,.2f}", 
    delta=f"Diferença: R$ {diferenca:,.2f}" if diferenca != 0 else "Valores Batem ✅",
    delta_color="off" if diferenca == 0 else "inverse"
)

if diferenca != 0 and meta_informada > 0:
    st.warning("⚠️ Atenção: O total informado não bate com a soma das colunas abaixo. Verifique os valores antes de considerar o resultado final.")

# --- BOTÃO DE CÁLCULO ---
st.markdown("---")
calcular = st.button("Calcular Previsão de Pagamento", type="primary")

if calcular:
    # 1. DEFINIÇÃO DA FAIXA (Baseada na Soma Total Real)
    # Faixas da Imagem:
    # Até 4.8M -> 0,16% | 0,045% | 0,045% (Total 0,25%)
    # Até 7.5M -> 0,16% | 0,070% | 0,070% (Total 0,30%)
    # Acima 7.5M -> 0,16% | 0,070% | 0,120% (Total 0,35%)

    pct_p1 = 0.0 # 1º Pagamento (Confirmação)
    pct_p2 = 0.0 # 2º Pagamento (Confirmação)
    pct_p3 = 0.0 # 3º Pagamento (Confirmação)
    nome_faixa = ""

    if soma_tabelas <= 4800000:
        nome_faixa = "Faixa 1 (Até 4.8 Milhões)"
        pct_p1, pct_p2, pct_p3 = 0.16, 0.045, 0.045
    elif soma_tabelas <= 7500000:
        nome_faixa = "Faixa 2 (Até 7.5 Milhões)"
        pct_p1, pct_p2, pct_p3 = 0.16, 0.070, 0.070
    else:
        nome_faixa = "Faixa 3 (Acima de 7.5 Milhões)"
        pct_p1, pct_p2, pct_p3 = 0.16, 0.070, 0.120

    st.subheader(f"📊 Parâmetros da Safra: {nome_faixa}")
    
    # 2. CÁLCULO PONDERADO POR TABELA E POR PARCELA
    # Estrutura: Lista de Tuplas (ValorVendido, Multiplicador)
    dados_calculo = [
        (v_tab1, 1.0), # Tabela 1
        (v_tab2, 1.0), # Tabela 2
        (v_tab3, 0.5), # Tabela 3 (50%)
        (v_tab4, 0.7)  # Tabela 4 (70%)
    ]

    # Acumuladores de valores monetários
    total_receber_p1 = 0.0
    total_receber_p2 = 0.0
    total_receber_p3 = 0.0

    for valor_venda, multiplicador in dados_calculo:
        if valor_venda > 0:
            # Aplica o multiplicador na porcentagem da parcela
            # Ex: Se a parcela é 0.16% e multiplicador é 0.5, vira 0.08%
            val_p1 = valor_venda * ((pct_p1 * multiplicador) / 100)
            val_p2 = valor_venda * ((pct_p2 * multiplicador) / 100)
            val_p3 = valor_venda * ((pct_p3 * multiplicador) / 100)

            total_receber_p1 += val_p1
            total_receber_p2 += val_p2
            total_receber_p3 += val_p3

    # 3. APLICAÇÃO DO DSR (25%) SOBRE AS PARCELAS
    # O supervisor recebe a parcela JÁ com DSR
    p1_com_dsr = total_receber_p1 * 1.25
    p2_com_dsr = total_receber_p2 * 1.25
    p3_com_dsr = total_receber_p3 * 1.25

    total_geral_comissao = p1_com_dsr + p2_com_dsr + p3_com_dsr

    # --- EXIBIÇÃO DOS RESULTADOS ---
    st.divider()
    st.header("💰 Fluxo de Recebimento Previsto")
    st.caption("Valores abaixo já incluem DSR de 25%")

    col_res1, col_res2, col_res3 = st.columns(3)
    
    col_res1.success(f"**1º Pagamento (Confirmação)**\n### R$ {p1_com_dsr:,.2f}")
    col_res1.markdown(f"*Base da Faixa: {pct_p1}%*")
    
    col_res2.info(f"**2º Pagamento**\n### R$ {p2_com_dsr:,.2f}")
    col_res2.markdown(f"*Base da Faixa: {pct_p2}%*")
    
    col_res3.info(f"**3º Pagamento**\n### R$ {p3_com_dsr:,.2f}")
    col_res3.markdown(f"*Base da Faixa: {pct_p3}%*")

    st.divider()
    col_total_final, _ = st.columns([1, 2])
    col_total_final.metric(
        "🏆 COMISSÃO TOTAL DA SAFRA", 
        f"R$ {total_geral_comissao:,.2f}",
        help="Soma das 3 parcelas com DSR incluso"
    )

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
