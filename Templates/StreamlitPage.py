import streamlit as st

st.title("Mapa Interativo no Streamlit")
st.write("Aqui estará o mapa interativo!")

# Exemplo de HTML para um mapa (pode ser substituído pelo mapa real)
html_code = """
    <iframe width="600" height="450" 
    src="https://maps.google.com/maps?q=São Paulo&t=&z=13&ie=UTF8&iwloc=&output=embed">
    </iframe>
"""
st.components.v1.html(html_code, height=500)

# Botão para voltar para a página inicial do Flask
if st.button("Voltar para Página Inicial"):
    st.markdown('<script type="text/javascript">window.location.href="http://localhost:5000/";</script>', unsafe_allow_html=True)
