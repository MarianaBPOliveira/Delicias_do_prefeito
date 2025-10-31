import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Loja de Doces 🍬", page_icon="🍫", layout="centered")

st.title("🍫 Delícias do Prefeito")
st.write("Escolha os doces desejados e finalize seu pedido!")

# ==============================
# CONFIGURAÇÕES
# ==============================
ARQUIVO_RELATORIO = "pedidos.csv"

# Doces unitários avulsos
DOCES_UNITARIOS = {
    "Brigadeiro (unidade)": 2.00,
    "Bem casado (unidade)": 2.00,
    "Docinho de Paçoca": 2.00,
    "Brigadeiro de Palha de Ninho com Oreo (unidade)": 2.00,
    "Palha Italiana de Ninho com Oreo (unidade)": 5.00,  # Novo doce avulso
    "Salgadinho de queijo": 5.00,
}

# Doces que podem ir na caixa
DOCES_CAIXA = {
    "Brigadeiro (unidade)": 2.00,
    "Bem casado (unidade)": 2.00,
    "Docinho de Paçoca": 2.00,
    "Brigadeiro de Palha de Ninho com Oreo (unidade)": 2.00,
}

CAIXA = {
    "Caixa de doces (4 unidades)": 7.00,
}

# ==============================
# FORMULÁRIO
# ==============================
st.header("🧁 Monte seu pedido")

nome = st.text_input("Seu nome completo")

pedidos = {}

# Seleção de doces unitários
st.subheader("Doces unitários")
for doce, preco in DOCES_UNITARIOS.items():
    qtd = st.number_input(f"{doce} — R$ {preco:.2f}", min_value=0, step=1, key=doce)
    if qtd > 0:
        pedidos[doce] = qtd

# Seleção de caixa de doces
st.subheader("Caixa de doces")
qtd_caixa = st.number_input(
    f"Caixa de doces (4 unidades) — R$ {CAIXA['Caixa de doces (4 unidades)']:.2f}",
    min_value=0, step=1, key="caixa"
)

# Se selecionou ao menos 1 caixa, permite escolher os 4 doces (somente dos doces permitidos)
caixas_selecionadas = []
if qtd_caixa > 0:
    st.info("Escolha 4 doces para cada caixa (somente Brigadeiro, Bem casado ou Brigadeiro de Palha de Ninho com Oreo)")
    for i in range(qtd_caixa):
        st.markdown(f"**Seleção da caixa #{i+1}:**")
        opcoes = {}
        for j in range(4):
            doce = st.selectbox(
                f"Doce {j+1} da caixa #{i+1}", 
                DOCES_CAIXA.keys(), 
                key=f"caixa_{i}_{j}"
            )
            opcoes[f"Doce {j+1}"] = doce
        caixas_selecionadas.append(opcoes)

# ==============================
# FINALIZAR PEDIDO
# ==============================
if st.button("✅ Finalizar Pedido"):
    if not nome.strip():
        st.error("Por favor, preencha seu nome antes de finalizar o pedido.")
    elif not pedidos and qtd_caixa == 0:
        st.error("Selecione ao menos um doce para finalizar o pedido.")
    else:
        # Calcula total
        total_unitario = sum(DOCES_UNITARIOS[d] * q for d, q in pedidos.items())
        total_caixa = CAIXA["Caixa de doces (4 unidades)"] * qtd_caixa
        total = total_unitario + total_caixa

        # Monta string do pedido
        pedidos_str = []
        for d, q in pedidos.items():
            pedidos_str.append(f"{d} (x{q})")
        for i, caixa in enumerate(caixas_selecionadas):
            doces_da_caixa = ", ".join(caixa.values())
            pedidos_str.append(f"Caixa #{i+1}: {doces_da_caixa}")

        novo_pedido = {
            "Nome": nome,
            "Pedidos": "; ".join(pedidos_str),
            "Total (R$)": round(total, 2),
            "Observação": "",
        }

        # Salva em CSV
        if os.path.exists(ARQUIVO_RELATORIO):
            df_existente = pd.read_csv(ARQUIVO_RELATORIO)
            df = pd.concat([df_existente, pd.DataFrame([novo_pedido])], ignore_index=True)
        else:
            df = pd.DataFrame([novo_pedido])

        df.to_csv(ARQUIVO_RELATORIO, index=False)
        st.success(f"Pedido de **{nome}** registrado com sucesso! 🍬 Total: R$ {total:.2f}")

# ==============================
# RELATÓRIO (VISUALIZAR)
# ==============================
st.markdown("---")
st.header("📋 Relatório de Pedidos")

total_df = pd.DataFrame(columns=["Doce", "Total de unidades pedido"])

if os.path.exists(ARQUIVO_RELATORIO):
    df = pd.read_csv(ARQUIVO_RELATORIO)
    st.dataframe(df, use_container_width=True)

    # Inicializa totais
    totais = {doce: 0 for doce in DOCES_UNITARIOS}

    for _, row in df.iterrows():
        # Contabiliza doces avulsos
        for d in DOCES_UNITARIOS:
            match = re.findall(rf"{re.escape(d)} \(x(\d+)\)", row["Pedidos"])
            if match:
                totais[d] += sum(int(x) for x in match)

        # Contabiliza doces dentro das caixas
        caixas = re.findall(r"Caixa #\d+: ([^;]+)", row["Pedidos"])
        for caixa in caixas:
            doces_da_caixa = [d.strip() for d in caixa.split(",")]
            for d in doces_da_caixa:
                if d in totais:
                    totais[d] += 1  # cada doce dentro da caixa conta como 1 unidade

    st.subheader("🍭 Totais por tipo de doce (incluindo caixas):")
    total_df = pd.DataFrame([{"Doce": d, "Total de unidades pedido": q} for d, q in totais.items()])
    st.table(total_df)

    # Botão para baixar o relatório de totais
    st.download_button(
        label="💾 Baixar Totais por tipo de doce",
        data=total_df.to_csv(index=False).encode("utf-8"),
        file_name="totais_doces.csv",
        mime="text/csv"
    )


else:
    st.info("Nenhum pedido foi registrado ainda.")




# ==============================
# BOTÃO PARA LIMPAR PEDIDOS
# ==============================
if os.path.exists(ARQUIVO_RELATORIO):
    st.markdown("---")
    if st.button("🗑️ Limpar TODOS os pedidos"):
        os.remove(ARQUIVO_RELATORIO)
        st.warning("Todos os pedidos foram apagados com sucesso!")
        st.stop()


if os.path.exists(ARQUIVO_RELATORIO):
    st.markdown("---")
    st.download_button(
        label="💾 Baixar relatório CSV",
        data=open(ARQUIVO_RELATORIO, "rb").read(),
        file_name="relatorio_pedidos.csv",
        mime="text/csv"
    )


