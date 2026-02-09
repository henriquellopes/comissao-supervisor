import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Simulador Supervisor - Detalhado",
    page_icon="👔",
    layout="wide"
)

st.title("👔 Calculadora de Comissão - Supervisor")
st.markdown("Cálculo com detalhamento por origem da venda e DSR.")

# --- 1. VALIDAÇÃO DE TOTAIS ---
st.header("1. Validação")
col_val1, col_val2 = st.columns([1, 2])
with col_val1:
    meta_informada = st.number_input(
        "Insira o TOTAL GERAL de vendas (R$):", 
        min_value=0.0, step=1000.0, format="%.2f"
    )

# --- 2. ENTRADA POR TABELA ---
st.header("2. Vendas por Tabela")

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    
    # Definição das tabelas e inputs
    with c1:
        st.info("1. BA, BMA, Est. 2%")
        st.caption("Mult: 1.0")
        v_tab1 = st.number_input("R$", min_value=0.0, key="t1")
    with c2:
        st.info("2. SELECT, PESADOS")
        st.caption("Mult: 1.0")
        v_tab2 = st.number_input("R$", min_value=0.0, key="t2")
    with c3:
        st.warning("3. Estendida 12x")
        st.caption("Mult: 0.5")
        v_tab3 = st.number_input("R$", min_value=0.0, key="t3")
    with c4:
        st.error("4. Estendida 1%")
        st.caption("Mult: 0.7")
        v_tab4 = st.number_input("R$", min_value=0.0, key="t4")

# Validação Visual
soma_tabelas = v_tab1 + v_tab2 + v_tab3 + v_tab4
diferenca = meta_informada - soma_tabelas

if meta_informada > 0:
    st.markdown("---")
    if diferenca == 0:
        st.success(f"✅ Total confere: R$ {soma_tabelas:,.2f}")
    else:
        st.warning(f"⚠️ Divergência: Informado R$ {meta_informada:,.2f} | Soma R$ {soma_tabelas:,.2f} (Dif: {diferenca:,.2f})")

# --- BOTÃO DE CÁLCULO ---
st.markdown("---")
calcular = st.button("Calcular Detalhamento", type="primary")

if calcular:
    # 1. DEFINIR A FAIXA (% BASE)
    # Regra: Até 4.8M (0.25%) | Até 7.5M (0.30%) | Acima (0.35%)
    # Parcelas (P1, P2, P3) baseadas na imagem
    
    if soma_tabelas <= 4800000:
        nome_faixa = "Faixa 1 (Até 4.8M)"
        pcts = [0.16, 0.045, 0.045] # P1, P2, P3
    elif soma_tabelas <= 7500000:
        nome_faixa = "Faixa 2 (Até 7.5M)"
        pcts = [0.16, 0.070, 0.070]
    else:
        nome_faixa = "Faixa 3 (Acima de 7.5M)"
        pcts = [0.16, 0.070, 0.120]

    st.subheader(f"📊 {nome_faixa}")

    # 2. CÁLCULO DETALHADO
    # Lista de configuração das tabelas
    tabelas_config = [
        {"nome": "1. BA/BMA", "valor": v_tab1, "mult": 1.0},
        {"nome": "2. SELECT", "valor": v_tab2, "mult": 1.0},
        {"nome": "3. Est. 12x", "valor": v_tab3, "mult": 0.5},
        {"nome": "4. Est. 1%", "valor": v_tab4, "mult": 0.7},
    ]

    # Estruturas para guardar o detalhamento de cada parcela
    # Cada uma vai ser uma lista de dicionarios: [{'nome': 'BA', 'valor': 500}, ...]
    detalhes_p1 = []
    detalhes_p2 = []
    detalhes_p3 = []

    total_base_p1 = 0.0
    total_base_p2 = 0.0
    total_base_p3 = 0.0

    for item in tabelas_config:
        if item["valor"] > 0:
            # Calcula a comissão desta tabela para cada parcela
            # Fórmula: ValorVenda * (PctParcela * MultiplicadorTabela)
            
            c_p1 = item["valor"] * ((pcts[0] * item["mult"]) / 100)
            c_p2 = item["valor"] * ((pcts[1] * item["mult"]) / 100)
            c_p3 = item["valor"] * ((pcts[2] * item["mult"]) / 100)

            # Guarda nos totais
            total_base_p1 += c_p1
            total_base_p2 += c_p2
            total_base_p3 += c_p3

            # Guarda no detalhamento
            detalhes_p1.append(f"**{item['nome']}**: R$ {c_p1:,.2f}")
            detalhes_p2.append(f"**{item['nome']}**: R$ {c_p2:,.2f}")
            detalhes_p3.append(f"**{item['nome']}**: R$ {c_p3:,.2f}")

    # 3. FUNÇÃO PARA EXIBIR O CARTÃO DE PAGAMENTO
    def mostrar_parcela(titulo, total_base, lista_detalhes, pct_ref):
        dsr = total_base * 0.25
        total_com_dsr = total_base + dsr
        
        # O Cartão visual principal
        st.info(f"**{titulo}**\n### R$ {total_com_dsr:,.2f}")
        st.caption(f"Ref. Faixa: {pct_ref}% + DSR")

        # O Expander com os detalhes
        with st.expander("Ver composição do valor"):
            st.markdown("###### Origem da Comissão:")
            for linha in lista_detalhes:
                st.write(linha)
            
            st.markdown("---")
            st.write(f"Subtotal: R$ {total_base:,.2f}")
            st.write(f"➕ **DSR (25%)**: R$ {dsr:,.2f}")
            st.markdown(f"**= Total: R$ {total_com_dsr:,.2f}**")

    # 4. EXIBIÇÃO NA TELA
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        mostrar_parcela("1º Pagamento (Confirmação)", total_base_p1, detalhes_p1, pcts[0])

    with col2:
        mostrar_parcela("2º Pagamento", total_base_p2, detalhes_p2, pcts[1])

    with col3:
        mostrar_parcela("3º Pagamento", total_base_p3, detalhes_p3, pcts[2])

    # Totalzão final
    st.divider()
    geral = (total_base_p1 + total_base_p2 + total_base_p3) * 1.25
    st.metric("🏆 TOTAL DA SAFRA (Soma das 3 parcelas)", f"R$ {geral:,.2f}")

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
